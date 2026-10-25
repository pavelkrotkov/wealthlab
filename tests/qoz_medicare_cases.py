"""Actual QOZ source-year correction crosses a supported future Medicare tier."""

from qoz_cases import flat

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.medicare_household_template import template
from wealthlab.tax.projection_example import template as taxes


def case():
    data = flat(2026, 3).model_dump(mode="json")
    data["lot_plan"]["case"]["trades"][0]["date"] = "2026-12-15"
    data["qoz_plan"]["calls"][0]["date"] = "2027-01-31"
    data["qoz_plan"]["prior_source_year_revision_assumed_confirmed"] = True
    data["incomes"] = [
        dict(
            id="source_year_salary",
            provenance="illustration",
            owner="person_a",
            start="2026-01-01",
            end="2027-01-01",
            monthly_amount="15000",
            currency="USD",
            annual_growth=0,
            stop_at_retirement=False,
        )
    ]
    for index, member in enumerate(data["members"]):
        member["birth_date"] = f"{1960 + index}-01-01"
    scenario = Scenario.model_validate(data)
    data["tax_plan"] = taxes(scenario).model_dump(mode="json")
    data["medicare_plan"] = template(scenario)
    coverage = data["medicare_plan"]["case"]
    coverage["complete_context"] = True
    for row in coverage["coverage"]:
        row["eligibility_confirmed"] = True
    for flag in (
        "direct_billing_without_benefit_withholding_confirmed",
        "costs_excluded_from_other_expenses_confirmed",
        "complete_household_tax_history_confirmed",
    ):
        data["medicare_plan"][flag] = True
    return Scenario.model_validate(data)
