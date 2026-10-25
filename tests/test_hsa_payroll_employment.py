"""Job loss stops payroll eligibility without borrowing later earnings or opening savings."""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_payroll_example import synthetic


def test_job_loss_changes_actual_salary_reduction_and_fica_bases():
    data = synthetic().model_dump(mode="json")
    data["employment_plan"] = dict(
        paths=[
            dict(
                id="work",
                provenance="assumption",
                owner="person_a",
                income_ids=[data["incomes"][0]["id"]],
                opening_multiplier=1,
                changes=[
                    dict(
                        id="loss",
                        provenance="assumption",
                        date="2026-07-01",
                        kind="job_loss",
                        multiplier=0,
                    )
                ],
            )
        ]
    )
    rows = project(Scenario.model_validate(data))
    assert sum(r["income"] for r in rows) == 60000
    assert sum(r["hsa_payroll_contributions"] for r in rows) == 3000
    assert sum(r["hsa_payroll_unfilled"] for r in rows) == 3000
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 44000
    assert rows[-1]["annual_tax"]["federal"]["employee_payroll"] == Decimal("4360.50")
    assert rows[-1]["annual_tax"]["new_jersey"]["gross_income"] == 48500
