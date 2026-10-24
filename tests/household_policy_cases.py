"""Complete synthetic policy inputs keep tests focused on real cash/holdings outcomes."""

from tests.market_household_cases import flat
from wealthlab.household.scenario import Scenario
from wealthlab.markets.policy_example import sale


def targets():
    case, market, binding = flat(cash_yield=0)
    data = case.model_dump(mode="json")
    data["lot_plan"]["case"]["sale_policies"] = [
        sale(i, when, ".5", "target_weight", dict(stock="999"))
        for i, when in enumerate(("2026-01-31", "2026-02-28"))
    ]
    return Scenario.model_validate(data), market, binding


def staged():
    from tests.test_market_household_inflation import spending_case

    case, market, binding = spending_case()
    data = case.model_dump(mode="json")
    data["expenses"][0]["monthly_amount"] = "2000"
    data["lot_plan"]["funding_sources"][0]["commission"] = "0"
    data["lot_plan"]["case"]["sale_policies"] = [
        sale(i, when, fraction, "original_fraction", dict(stock="100"))
        for i, (when, fraction) in enumerate((("2026-02-28", ".02"), ("2026-03-31", ".03")))
    ]
    return Scenario.model_validate(data), market, binding
