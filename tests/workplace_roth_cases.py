"""One consistent member/payroll/tax age context for qualification boundary checks."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_roth_example import synthetic
from wealthlab.tax.projection_example import template


def aged_data(born):
    data = synthetic().model_dump(mode="json")
    data["members"][0]["birth_date"] = born
    for context in data["workplace_plan"]["years"]:
        context["contributors"][0]["birth_date"] = born
    data["tax_plan"] = template(Scenario.model_validate(data)).model_dump(mode="json")
    return data


def payroll_data(wages):
    from wealthlab.household.example import synthetic as working

    data = synthetic().model_dump(mode="json")
    data["accounts"][1]["balance"] = 0
    plan = data["workplace_plan"]
    contract = plan["roth_cash_withdrawals"]["contracts"]["ordinary"]
    contract.update(
        separation_date="2026-02-01",
        first_federal_contribution_year=None,
        federal_basis=0,
        nj_basis=0,
    )
    plan["years"][0]["contributors"][0].update(
        workplace_eligible=True,
        workplace_compensation=10000,
    )
    plan["orders"] = [
        dict(
            id="new_roth_principal",
            provenance="illustration",
            date="2026-01-15",
            owner="person_a",
            destination="work_roth",
            kind="roth_401k",
            amount=2000,
        )
    ]
    salary = working().incomes[0].model_dump(mode="json")
    salary.update(
        monthly_amount=wages, start="2026-01-01", end="2026-02-01", stop_at_retirement=False
    )
    data["incomes"] = [salary]
    data["tax_plan"] = template(Scenario.model_validate(data)).model_dump(mode="json")
    return data
