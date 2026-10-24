"""An independently synthetic retired household, with benefits and interest counted once."""

from datetime import date

from wealthlab.household.example import synthetic as household
from wealthlab.household.records import Member
from wealthlab.household.scenario import Scenario
from wealthlab.household.schedules import Income
from wealthlab.retirement.social_example import synthetic as claims
from wealthlab.tax.projection_example import template
from wealthlab.tax.projection_inputs import IncomeRule


def synthetic():
    social = claims()
    case = household()
    payload = case.model_dump()
    payload.update(
        name="Synthetic retired household with Social Security",
        start=date(2030, 1, 1),
        end=date(2033, 1, 1),
        inflation=0,
        members=[
            Member(
                id=p.id,
                provenance="illustration",
                birth_date=p.birth_date,
                retirement_date=date(2029, 1, 1),
            )
            for p in social.members
        ],
        accounts=[
            a.model_copy(update=dict(owner="joint" if a.owner == "joint" else "person"))
            for a in case.accounts
        ],
        incomes=[
            Income(
                id="interest",
                provenance="illustration",
                owner="person",
                start=date(2030, 1, 1),
                end=date(2033, 1, 1),
                monthly_amount=1000,
                currency="USD",
                annual_growth=0,
                stop_at_retirement=False,
            )
        ],
        expenses=[
            e.model_copy(update=dict(start=date(2030, 1, 1), end=date(2033, 1, 1)))
            for e in case.expenses
        ],
        social_security=social,
    )
    result = Scenario.model_validate(payload)
    plan = template(result).model_copy(
        update=dict(
            income_rules=[
                IncomeRule(income_id="interest", federal="interest", new_jersey="interest")
            ]
        )
    )
    return result.model_copy(update=dict(tax_plan=plan))
