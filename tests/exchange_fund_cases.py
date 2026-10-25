"""Compact original synthetic conditional cases; no sponsor contract is implied."""

from datetime import date

from wealthlab.household.scenario import Scenario
from wealthlab.products.exchange_fund_example import request, synthetic


def flat():
    data = synthetic().model_dump(mode="json")
    data.update(end="2027-01-01", expenses=[])
    plan = data["exchange_fund_plan"]
    plan.update(annual_fee="0", liquid_after="2026-12-01")
    plan["observations"] = plan["observations"][:12]
    plan["requests"] = [
        request("release", date(2026, 12, 31), "redeem"),
        request("sale", date(2026, 12, 31), "sell_liquid"),
    ]
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    return Scenario.model_validate(data)


def change(case, configure):
    data = case.model_dump(mode="json")
    configure(data)
    return Scenario.model_validate(data)
