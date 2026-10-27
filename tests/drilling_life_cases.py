"""Original supplied policy and drilling paths compete for one actual wallet."""

from wealthlab.household.scenario import Scenario
from wealthlab.products.drilling_example import synthetic as drilling
from wealthlab.products.life_household_example import event
from wealthlab.products.life_household_example import synthetic as life


def blended(loan=False):
    data = life().model_dump(mode="json")
    data.update(end="2026-02-01", expenses=[])
    data["accounts"][0]["balance"] = "99500" if loan else "100500"
    source = drilling().model_dump(mode="json")
    data["accounts"].append(source["accounts"][1])
    data["drilling_plan"] = source["drilling_plan"]
    data["drilling_plan"]["observations"] = source["drilling_plan"]["observations"][:1]
    holding = data["life_plan"]["holdings"][0]
    if loan:
        holding["contract"].update(
            federal_status="mec",
            opening_federal_basis="8000",
            events=[event("loan", "2026-01-15", "loan_advance", 500, cash_value_before="10000")],
        )
        holding["contract"]["values"][0].update(
            gross_cash_value="10000", gross_surrender_value="10000"
        )
        holding["failure_exits"] = {}
    return Scenario.model_validate(data)
