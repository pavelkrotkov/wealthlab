"""One shared IRA opening context for contribution/rollover coexistence checks."""

from wealthlab.retirement.ira_contribution_example import synthetic as contributions
from wealthlab.retirement.ira_rollover_example import synthetic


def combined(cash):
    data = synthetic().model_dump(mode="json")
    data["orders"] = []
    plan = contributions().model_dump(mode="json")["contributions"]
    plan["opening_cash"] = data["opening_cash"] = cash
    plan["contributors"][0]["birth_date"] = data["owners"][0]["birth_date"]
    plan["accounts"] = [{k: v for k, v in a.items() if k != "product"} for a in data["accounts"]]
    for order in plan["orders"]:
        order["date"] = "2026-04-01"
    data.update(contributions=plan, contribution_context_confirmed=True)
    return data
