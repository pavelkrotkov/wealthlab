"""Combined original synthetic books with matched horizons and separately owned capital."""

from wealthlab.household.scenario import Scenario
from wealthlab.products.exchange_fund_example import synthetic as exchange_example
from wealthlab.products.option_household_example import synthetic as option_example


def combined():
    data = option_example().model_dump(mode="json")
    exchange = exchange_example().model_dump(mode="json")
    data["accounts"].append(exchange["accounts"][1])
    plan = exchange["exchange_fund_plan"]
    plan["observations"] = plan["observations"][:12]
    plan["requests"] = []
    data["exchange_fund_plan"] = plan
    return data


def overlapping():
    data = combined()
    plan = data["exchange_fund_plan"]
    plan["account_id"] = "options"
    plan["source_lot"].update(
        account_id="options", quantity="100", federal_basis="2000", nj_basis="3000"
    )
    plan["contribution_quantity"] = "100"
    return Scenario.model_validate(data)
