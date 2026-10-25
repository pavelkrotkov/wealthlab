"""Disjoint synthetic fund accounts share one cash wallet and one annual return."""

from exchange_fund_cases import flat as exchange
from private_fund_cases import fund, request

from wealthlab.household.scenario import Scenario


def combined():
    data = exchange().model_dump(mode="json")
    sleeve = fund(
        federal_opening_basis="80000",
        new_jersey_opening_basis="90000",
        requests=[request(final=True, notice="2026-12-01")],
    )
    data["accounts"].append(sleeve.accounts[1].model_dump(mode="json"))
    data["sleeve_plan"] = sleeve.sleeve_plan.model_dump(mode="json")
    data["name"] = "Synthetic mixed private and exchange funds"
    return Scenario.model_validate(data)
