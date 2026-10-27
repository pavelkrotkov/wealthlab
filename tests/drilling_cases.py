"""Small original synthetic drilling cases isolate actual money from assumed tax qualification."""

from datetime import date

from wealthlab.household.scenario import Scenario
from wealthlab.products.drilling_example import synthetic


def short(count=1):
    data = synthetic().model_dump(mode="json")
    data.update(end=date(2026, count + 1, 1).isoformat(), incomes=[], expenses=[])
    plan = data["drilling_plan"]
    plan["residual_federal_capital_character"] = "short_term"
    plan["observations"] = plan["observations"][:count]
    for row in plan["observations"]:
        row["supplemental_federal"] = {}
    plan["observations"][-1].update(
        exit_requested=True,
        exit_gross_proceeds="40000",
        distribution_request="0",
        reference_cash_request="0",
    )
    data["tax_plan"]["income_rules"] = []
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    return Scenario.model_validate(data)


def change(case, configure):
    data = case.model_dump(mode="json")
    configure(data)
    return Scenario.model_validate(data)
