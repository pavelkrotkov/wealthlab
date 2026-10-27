"""Original new-cash covered call; native purchase creates its shares and actual tax bases."""

from wealthlab.household.scenario import Scenario
from wealthlab.products.option_household_example import synthetic as existing_example
from wealthlab.products.option_household_inputs import OptionPlan


def unit_plan():
    data = existing_example().option_plan.model_dump(mode="json")
    case = data["case"]
    case["holdings"]["lots"] = []
    case["holdings"]["accounts"][0]["cash"] = "12000"
    case["opening_stock_purchase"] = dict(
        id="new_stock", provenance="illustration", date="2026-01-01", shares=100, fee="2"
    )
    case["legs"][0].update(opening_fee="1", closing_fee="1")
    case["stock_sale_fee"] = "1"
    return OptionPlan.model_validate(data)


def synthetic():
    data = existing_example().model_dump(mode="json")
    data["name"] = "Synthetic new-cash stock purchase and covered call"
    data["option_plan"] = unit_plan().model_dump(mode="json")
    data["accounts"][1]["balance"] = "12000"
    return Scenario.model_validate(data)
