"""Invented history and explicit named stresses, never provider performance data."""

from wealthlab.markets.household_example import synthetic as market_household
from wealthlab.markets.stresses import NAMES
from wealthlab.optimization.example import synthetic as ordinary
from wealthlab.optimization.inputs import PolicySearch


def synthetic():
    data = ordinary().model_dump(mode="json")
    checks = {
        mode: dict(market=market_household(mode)[1].model_dump(mode="json"), required=True)
        for mode in ("deterministic", "historical")
    }
    checks.update(
        {
            name: dict(
                market=market_household("stress", name)[1].model_dump(mode="json"), required=True
            )
            for name in NAMES
        }
    )
    data["binding"]["inflation_expenses"] = ["living"]
    data["robustness"] = checks
    return PolicySearch.model_validate(data)
