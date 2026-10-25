"""Synthetic presets reuse the existing realized-path generator and public audit format."""

from wealthlab.markets.household_example import synthetic as markets
from wealthlab.markets.inputs import MarketCase
from wealthlab.products.life_allocation_example import synthetic as new_issue
from wealthlab.products.life_comparison_example import synthetic as alternatives
from wealthlab.products.life_comparison_existing import synthetic as existing_policy


def synthetic(mode="entered", existing=False, uninsured=False):
    case = new_issue() if uninsured else existing_policy() if existing else alternatives()
    if mode == "entered":
        return case
    _, market, binding = markets(mode)
    scenario = next(iter(case.alternatives.values()))
    data = market.model_dump(mode="json")
    data.update(start=str(scenario.start), end=str(scenario.end))
    if data["historical"] is not None:
        data["historical"]["months"] = data["historical"]["months"][:3]
    data["shocks"] = [s for s in data["shocks"] if s["month"] < 3]
    return case.model_copy(update=dict(market=MarketCase.model_validate(data), binding=binding))
