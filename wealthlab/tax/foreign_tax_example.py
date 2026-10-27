"""Synthetic opening income and an actual foreign tax payment share one wallet.

Opening cash already reflects prior recognized wages and paid payroll. The
remaining income tax and foreign assessment are paid during the projection;
no prior wages or source withholding are deposited a second time.
"""

from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_credit_example import synthetic as credit_example


def synthetic():
    data = household().model_dump(mode="json")
    profile = credit_example().model_dump(mode="json")
    base = profile["annual"]
    base["payments"]["federal_income_withheld"] = "0"
    profile.update(tax_cash=[])
    data.update(
        name="Synthetic actual foreign tax cash and US credits",
        start="2025-10-01",
        end="2026-01-01",
        incomes=[],
        expenses=[],
        debts=[],
        contributions=[],
        members=[dict(data["members"][0], birth_date="1985-01-02")],
        accounts=[dict(data["accounts"][0], owner="person_a", balance="50000")],
        tax_plan=dict(
            cases=[base],
            income_rules=[],
            federal_wage_withholding="0",
            nj_wage_withholding="0",
            state_deduction_mode="entered",
        ),
    )
    data["foreign_tax_plan"] = foreign_plan(profile)
    return Scenario.model_validate(data)


def foreign_plan(profile):
    return dict(
        assessments=[
            dict(
                id="es_income_2025",
                owner_id="person_a",
                country="ES",
                liability_year=2025,
                tax_type="income",
                currency="EUR",
                observed="2025-10-01",
                amount_native="10000",
                eligibility="allowed",
                source="Invented confirmed ordinary income-tax assessment; no residence conclusion",
            )
        ],
        schedules=[
            dict(
                id="es_installment",
                assessment_id="es_income_2025",
                due_date="2025-10-31",
                requested_native="10000",
                basket="general",
                creditable_fraction="1",
                credit_eligibility="allowed",
                included_income_confirmed=True,
                source_income_year=2025,
                income_ids=["work_es"],
                source="Synthetic remaining tax; not sponsor or filing terms",
            )
        ],
        quotes=[
            dict(
                date=when,
                currency="EUR",
                usd_per_unit="1.10",
                source="Invented dated spot quote for cash settlement and remaining assessment",
            )
            for when in ("2025-10-31", "2025-11-30", "2025-12-31")
        ],
        credit_profiles=[profile],
        source="Synthetic cash execution; independent mainland NJ facts",
    )
