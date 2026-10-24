"""Use NumPy's validated joint sampling once, then reuse the realized batch.

Expected mark return is an arithmetic annual expectation, independent of cash
yield. Lognormal monthly drift preserves that one-year expected mark growth.
Annual volatility belongs to log returns; correlations are between monthly
log shocks, with inflation last. These are explicit model assumptions, not
claims about tail behavior or future market performance.
"""

import hashlib
import json
from dataclasses import dataclass

import numpy as np

from wealthlab.household.calendar import months


@dataclass(frozen=True)
class PathBatch:
    dates: tuple
    assets: tuple
    mark_returns: np.ndarray
    cash_yields: np.ndarray
    inflation: np.ndarray
    locked: np.ndarray
    metadata: dict

    def export(self):
        return dict(
            dates=[d.isoformat() for d in self.dates],
            assets=self.assets,
            mark_returns=self.mark_returns.tolist(),
            cash_yields=self.cash_yields.tolist(),
            inflation=self.inflation.tolist(),
            locked=self.locked.tolist(),
            metadata=self.metadata,
        )


def generate(case):
    dates = tuple(a for a, _ in months(case.start, case.end))
    assets = tuple(a.id for a in case.assets)
    values = observations(case, len(dates))
    marks, inflation = values[:, :, :-1], values[:, :, -1]
    yields = cash_yields(case, marks.shape)
    locked = np.zeros((len(dates), len(assets)), dtype=bool)
    for shock in case.shocks:
        overlay(shock, assets, marks, inflation, locked)
    if not np.isfinite(values).all():
        raise ValueError("Market path overflow; reduce volatility or horizon.")
    metadata = provenance(case, marks, yields, inflation, locked)
    for array in (marks, yields, inflation, locked):
        array.setflags(write=False)
    return PathBatch(dates, assets, marks, yields, inflation, locked, metadata)


def observations(case, count):
    if case.mode == "historical":
        return np.array(
            [
                [*[r.mark_returns[a.id] for a in case.assets], r.inflation]
                for r in case.historical.months
            ],
            dtype=float,
        )[None, :, :]
    means = np.array(
        [a.expected_annual_mark_return for a in case.assets] + [case.expected_annual_inflation]
    )
    monthly_growth = np.log1p(means) / 12
    if not case.stochastic:
        return np.broadcast_to(np.expm1(monthly_growth), (1, count, len(means))).copy()
    sigma = np.array(
        [a.annual_volatility for a in case.assets] + [case.annual_inflation_volatility]
    )
    covariance = np.asarray(case.correlation) * np.outer(sigma, sigma) / 12
    rng = np.random.Generator(np.random.PCG64(case.seed))
    logs = rng.multivariate_normal(
        monthly_growth - sigma**2 / 24,
        covariance,
        size=(case.paths, count),
        check_valid="raise",
        tol=1e-12,
        method="eigh",
    )
    return np.expm1(logs)


def cash_yields(case, shape):
    if case.mode == "historical":
        return np.array(
            [[r.cash_yields[a.id] for a in case.assets] for r in case.historical.months],
            dtype=float,
        )[None, :, :]
    return np.broadcast_to([a.annual_cash_yield / 12 for a in case.assets], shape).copy()


def overlay(shock, assets, marks, inflation, locked):
    for identity, rate in shock.mark_shocks.items():
        index = assets.index(identity)
        marks[:, shock.month, index] = (1 + marks[:, shock.month, index]) * (1 + rate) - 1
    if shock.inflation_override is not None:
        inflation[:, shock.month] = shock.inflation_override
    for identity, duration in shock.lock_months.items():
        locked[shock.month : shock.month + duration, assets.index(identity)] = True


def provenance(case, marks, yields, inflation, locked):
    inputs = case.model_dump_json()
    digest = hashlib.sha256(inputs.encode())
    for array in (marks, yields, inflation, locked):
        digest.update(array.tobytes())
    return dict(
        batch_id=digest.hexdigest(),
        algorithm=("monthly-lognormal-pcg64-eigh-v1" if case.stochastic else case.mode + "-v1"),
        numpy_version=np.__version__,
        mode=case.mode,
        seed=case.seed,
        return_convention=case.return_convention,
        input=json.loads(inputs),
        historical_synthetic=case.historical.synthetic if case.historical else None,
    )
