"""Synthetic ordinary payroll and SSA checks share one cash/tax book without future wage access."""

from datetime import date
from decimal import Decimal

from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.social_work_example import synthetic as claims
from wealthlab.tax.projection_example import template


def synthetic():
    example = claims()
    raw = household().model_dump(mode="json")
    raw.update(
        name="Synthetic Social Security with earned wages",
        start="2026-01-01",
        end="2033-01-01",
        inflation=0,
        members=[
            dict(
                id="worker",
                provenance="illustration",
                birth_date="1964-01-02",
                retirement_date="2027-01-01",
            )
        ],
        accounts=[
            dict(
                id="cash",
                provenance="illustration",
                owner="worker",
                currency="USD",
                wrapper="cash",
                balance=10000,
                monthly_fee=0,
            )
        ],
        incomes=[
            income("january-wages", "2026-01-01", "2026-02-01", 3842),
            income("regular-wages", "2026-02-01", "2027-01-01", 2400),
        ],
        expenses=[
            dict(
                id="spending",
                provenance="illustration",
                category="essential",
                start="2026-01-01",
                end="2033-01-01",
                monthly_amount=500,
                currency="USD",
                annual_growth=0,
            )
        ],
        debts=[],
        contributions=[],
        social_security=example.claims.model_dump(mode="json"),
        social_work_plan=example.work.model_dump(mode="json"),
    )
    for report in raw["social_work_plan"]["years"]:
        report["actual_monthly_wages"] = None
    case = Scenario.model_validate(raw)
    plan = template(case).model_copy(
        update=dict(federal_wage_withholding=Decimal(0), nj_wage_withholding=Decimal(0))
    )
    return case.model_copy(update=dict(tax_plan=plan))


def income(identifier, start, end, value):
    return dict(
        id=identifier,
        provenance="illustration",
        owner="worker",
        start=date.fromisoformat(start),
        end=date.fromisoformat(end),
        monthly_amount=value,
        currency="USD",
        annual_growth=0,
        stop_at_retirement=True,
    )
