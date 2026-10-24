"""Fail on ambiguous return units, missing months and invalid joint correlation.

The last correlation row/column always belongs to inflation. A zero volatility
factor still needs a valid correlation declaration; it cannot hide an invalid
model. Historical replay uses a supplied past window without filling gaps,
cycling observations or consulting values unavailable at the decision date.
"""

import numpy as np

from wealthlab.household.calendar import months
from wealthlab.markets.history import validate_history


def validate(case):
    count = validate_dates(case)
    ids = validate_assets(case)
    validate_correlation(case.correlation, len(ids) + 1)
    validate_mode(case, count, ids)
    validate_shocks(case, count, set(ids))


def validate_dates(case):
    if case.start.day != 1 or case.end.day != 1 or case.end <= case.start:
        raise ValueError("Market paths require complete calendar months and an exclusive end.")
    count = len(list(months(case.start, case.end)))
    if count > 1200:
        raise ValueError("Market paths support at most 1200 months.")
    validate_path_count(case)
    paths = case.paths
    if count * paths * (len(case.assets) + 1) > 2000000:
        raise ValueError("Reduce paths or horizon to at most 2 million factor observations.")
    return count


def validate_correlation(values, size):
    matrix = np.asarray(values, dtype=float)
    if matrix.shape != (size, size) or not np.isfinite(matrix).all():
        raise ValueError("Correlation must be a finite square matrix including inflation last.")
    if not np.allclose(matrix, matrix.T, rtol=0, atol=1e-12):
        raise ValueError("Correlation must be symmetric.")
    if not np.allclose(np.diag(matrix), 1, rtol=0, atol=1e-12) or np.max(np.abs(matrix)) > 1:
        raise ValueError("Correlation requires unit diagonal and values between -1 and 1.")
    if np.linalg.eigvalsh(matrix).min() < -1e-12:
        raise ValueError("Correlation must be positive semidefinite.")


def validate_shocks(case, count, ids):
    if (case.mode == "stress") != bool(case.shocks):
        raise ValueError("Named stress events belong only in stress mode and cannot be empty.")
    for shock in case.shocks:
        if shock.month >= count:
            raise ValueError("A market stress must begin inside the projection horizon.")
        if (set(shock.mark_shocks) | set(shock.lock_months)) - ids:
            raise ValueError("Market stress references an unknown asset.")


def validate_assets(case):
    ids = [a.id for a in case.assets]
    if len(ids) != len(set(ids)) or "inflation" in ids:
        raise ValueError("Market asset IDs must be unique and cannot use reserved inflation.")
    if any(a.provenance == "unresolved" for a in case.assets):
        raise ValueError("Resolve critical market assumptions before generating paths.")
    validate_yield_convention(case)
    return set(ids)


def validate_mode(case, count, ids):
    if case.mode == "historical":
        validate_history(case, count, ids)
    elif case.historical is not None:
        raise ValueError("Historical data must be used in historical mode.")


def validate_path_count(case):
    if not case.stochastic and case.paths != 1:
        raise ValueError("Nonstochastic modes use exactly one path.")
    if case.mode != "stress" and case.stress_base != "deterministic":
        raise ValueError("A stress base is selected only in stress mode.")


def validate_yield_convention(case):
    if case.return_convention == "total_return_reinvested" and any(
        a.annual_cash_yield for a in case.assets
    ):
        raise ValueError("Reinvested total returns cannot also distribute cash yield.")
