"""Original price-only factors for one selected realized path; no manager return claim."""

import numpy as np

from wealthlab.markets.inputs import MarketCase


def synthetic(scenario, mode="deterministic"):
    ids = list(scenario.exchange_fund_plan.opening_prices)
    return MarketCase(
        start=scenario.start,
        end=scenario.end,
        mode=mode,
        seed=42,
        paths=20 if mode == "monte_carlo" else 1,
        assets=[
            dict(
                id=identity,
                provenance="illustration",
                role="equity",
                expected_annual_mark_return=0.04,
                annual_volatility=0.18,
                annual_cash_yield=0,
            )
            for identity in ids
        ],
        return_convention="price_plus_cash",
        expected_annual_inflation=0,
        annual_inflation_volatility=0,
        correlation=np.eye(len(ids) + 1).tolist(),
        shocks=[
            dict(
                name="Synthetic basket drawdown",
                month=3,
                mark_shocks={identity: -0.4 for identity in ids[1:]},
            )
        ]
        if mode == "stress"
        else [],
    )
