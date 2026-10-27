"""Shared timing with separately supplied home marks; no inferred property factor returns."""

from wealthlab.household.property_example import synthetic as home
from wealthlab.markets.household_example import synthetic as market_example
from wealthlab.markets.inputs import MarketCase


def synthetic(mode="deterministic", stress="early_crash"):
    household = home()
    _, market, binding = market_example(mode, stress)
    # The market batch still controls inflation/path reporting. Complete sourced
    # home marks and the closing quote retain their separate stated assumptions.
    data = market.model_dump(mode="json")
    data["end"] = household.end.isoformat()
    if data["historical"] is not None:
        data["historical"]["months"] = data["historical"]["months"][:12]
    data["shocks"] = [row for row in data["shocks"] if row["month"] < 12]
    market = MarketCase.model_validate(data)
    return household, market, binding.model_copy(update=dict(securities=[]))
