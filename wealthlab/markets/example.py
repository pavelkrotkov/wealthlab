"""Independent synthetic factors; historical mode uses invented observations only."""

from datetime import date

import numpy as np

from wealthlab.household.calendar import months
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.stresses import events


def synthetic(mode="monte_carlo", stress="early_crash"):
    data = dict(
        start="2027-01-01",
        end="2037-01-01",
        mode=mode,
        seed=42,
        paths=250 if mode == "monte_carlo" else 1,
        assets=[
            asset("equities", "equity", 0.05, 0.18, 0.02),
            asset("bonds", "bond", 0.01, 0.06, 0.03),
            asset("employer", "employer", 0.05, 0.35, 0),
        ],
        return_convention="price_plus_cash",
        expected_annual_inflation=0.025,
        annual_inflation_volatility=0.015,
        correlation=[
            [1, -0.1, 0.7, 0.1],
            [-0.1, 1, -0.1, -0.2],
            [0.7, -0.1, 1, 0.1],
            [0.1, -0.2, 0.1, 1],
        ],
    )
    if mode == "historical":
        data["historical"] = invented_history()
    if mode == "stress":
        base = MarketCase.model_validate({**data, "mode": "deterministic"})
        data["shocks"] = events(base, stress)
    return MarketCase.model_validate(data)


def asset(identity, role, mean, volatility, cash_yield):
    return dict(
        id=identity,
        provenance="illustration",
        role=role,
        expected_annual_mark_return=mean,
        annual_volatility=volatility,
        annual_cash_yield=cash_yield,
    )


def invented_history():
    rows = []
    for i, (when, _) in enumerate(months(date(2000, 1, 1), date(2010, 1, 1))):
        rows.append(
            dict(
                date=when,
                mark_returns=dict(
                    equities=0.004 + 0.03 * np.sin(i),
                    bonds=0.001,
                    employer=0.004 + 0.06 * np.sin(i),
                ),
                cash_yields=dict(equities=0.02 / 12, bonds=0.03 / 12, employer=0),
                inflation=0.002,
            )
        )
    return dict(
        source="Invented mathematical observations; not actual market history",
        retrieved_on="2026-10-24",
        available_as_of="2010-01-01",
        synthetic=True,
        months=rows,
    )
