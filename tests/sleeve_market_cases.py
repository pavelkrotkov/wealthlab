"""One-year flat joint factors isolate the household sleeve binding and safety consequences."""

from household_sleeve_cases import flat

from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.sleeve_example import synthetic


def baseline():
    _, market, binding = synthetic()
    household = flat()
    data = market.model_dump(mode="json")
    data.update(end=str(household.end), expected_annual_inflation=0)
    for asset in data["assets"]:
        asset.update(expected_annual_mark_return=0, annual_cash_yield=0)
    return household, MarketCase.model_validate(data), binding
