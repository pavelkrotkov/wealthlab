"""A flat synthetic security makes price/cash conservation independently checkable."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_example import synthetic
from wealthlab.markets.inputs import MarketCase


def flat(cash_yield=0.12):
    household, market, binding = synthetic()
    data = household.model_dump(mode="json")
    data.update(incomes=[], expenses=[])
    data["tax_plan"]["income_rules"] = []
    inputs = market.model_dump(mode="json")
    inputs["assets"][0].update(expected_annual_mark_return=0, annual_cash_yield=cash_yield)
    inputs.update(expected_annual_inflation=0)
    return Scenario.model_validate(data), MarketCase.model_validate(inputs), binding
