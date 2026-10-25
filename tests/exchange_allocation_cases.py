"""Original flat-price allocation controls with one actual retained-source terminal request."""

from datetime import date

from exchange_fund_cases import flat

from wealthlab.household.scenario import Scenario
from wealthlab.products.exchange_fund_example import request


def allocated(quantity, source_sale=True):
    data = flat().model_dump(mode="json")
    plan = data["exchange_fund_plan"]
    plan["contribution_quantity"] = str(quantity)
    if source_sale:
        plan["requests"].append(request("sell_source", date(2026, 12, 31), "sell_source"))
    return Scenario.model_validate(data)
