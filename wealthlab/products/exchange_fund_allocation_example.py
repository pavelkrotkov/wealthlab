"""Original zero/partial/full contribution profiles retain the same actual source capital."""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.scenario import Scenario
from wealthlab.products.exchange_fund_example import request, synthetic

CHOICES = ("Full contribution", "Partial contribution", "Retained source only")


def allocation_example(choice):
    scenario = synthetic()
    data = scenario.model_dump(mode="json")
    plan = data["exchange_fund_plan"]
    if choice == "Full contribution":
        return Scenario.model_validate(data)
    if choice == "Partial contribution":
        plan["contribution_quantity"] = str(Decimal(plan["source_lot"]["quantity"]) / 2)
    elif choice == "Retained source only":
        plan["contribution_quantity"] = "0"
    else:
        raise ValueError("Select a known synthetic contribution profile.")
    plan["requests"].append(
        request("sell_retained_source", scenario.end - timedelta(days=1), "sell_source")
    )
    return Scenario.model_validate(data)
