"""A deliberately synthetic salary reduction followed by job loss, with annual tax cash flows."""

from datetime import date
from decimal import Decimal

from wealthlab.employment.inputs import EmploymentPlan, WageChange, WagePath
from wealthlab.household.example import synthetic as household
from wealthlab.tax.projection_example import template as tax_template


def synthetic():
    case = household()
    path = WagePath(
        id="job_policy",
        provenance="illustration",
        owner="person_a",
        income_ids=["salary"],
        opening_multiplier=Decimal(1),
        changes=[
            WageChange(
                id="reduced_hours",
                provenance="illustration",
                date=date(2026, 7, 1),
                kind="pay_change",
                multiplier=Decimal(".5"),
            ),
            WageChange(
                id="job_loss",
                provenance="illustration",
                date=date(2026, 10, 1),
                kind="job_loss",
                multiplier=Decimal(0),
            ),
        ],
    )
    return case.model_copy(
        update=dict(
            name="Synthetic reduced work then job loss",
            tax_plan=tax_template(case),
            employment_plan=EmploymentPlan(paths=[path]),
        )
    )


def template(scenario):
    plan = scenario.tax_plan or tax_template(scenario)
    wages = {r.income_id for r in plan.income_rules if r.federal.startswith("wages_")}
    return dict(
        paths=[
            dict(
                id=f"work_path_{index}",
                provenance="assumption",
                owner=income.owner,
                income_ids=[income.id],
                opening_multiplier="1",
                changes=[],
            )
            for index, income in enumerate(scenario.incomes)
            if income.id in wages
        ]
    )
