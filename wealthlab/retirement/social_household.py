"""Materialize claim cash as ordinary household income, preserving one source of benefits.

The claim model already determines following-month, whole-dollar cash. Reuse
those amounts with zero growth; applying household inflation or retirement
cutoffs again would change them. The original scenario remains exportable.
"""

from datetime import date

from wealthlab.household.schedules import Income
from wealthlab.retirement.medicare_household_inputs import withholding
from wealthlab.retirement.social import run
from wealthlab.retirement.social_dates import shift
from wealthlab.retirement.social_household_validation import validate
from wealthlab.tax.projection_inputs import IncomeRule


def prepare(scenario):
    if scenario.social_security is None:
        return scenario
    result = run(scenario.social_security)
    validate(scenario, result)
    if withholding(scenario):
        return scenario
    incomes, rules = [], []
    for index, row in enumerate(result["cash_months"]):
        when = row["payment_month"]
        if not scenario.start <= when < scenario.end or not row["issued_before_offsets"]:
            continue
        identifier = f"ss_{index}_{when:%Y%m}"
        incomes.append(
            Income(
                id=identifier,
                provenance="assumption",
                owner=row["member"],
                start=when,
                end=shift(when, 1),
                monthly_amount=row["issued_before_offsets"],
                currency="USD",
                annual_growth=0,
                stop_at_retirement=False,
            )
        )
        rules.append(IncomeRule(income_id=identifier, federal="social_security", new_jersey="none"))
    plan = scenario.tax_plan.model_copy(
        update=dict(income_rules=[*scenario.tax_plan.income_rules, *rules])
    )
    payload = scenario.model_dump()
    payload.update(incomes=[*scenario.incomes, *incomes], tax_plan=plan, social_security=None)
    return type(scenario).model_validate(payload)


def template(scenario):
    """Unresolved PIAs/eligibility block a personalized calculation until edited."""
    from wealthlab.retirement.social_dates import seventieth_month
    from wealthlab.retirement.social_example import synthetic
    from wealthlab.retirement.social_inputs import SocialPerson

    members = [
        SocialPerson(
            id=person.id,
            provenance="unresolved",
            birth_date=person.birth_date,
            pia_january_2026=0,
            own_insured=False,
            claim_month=seventieth_month(person.birth_date),
            partner=None,
            spousal_eligibility_confirmed=False,
        )
        for person in scenario.members
    ]
    payload = synthetic().model_dump(mode="json")
    payload.update(
        start_year=scenario.start.year,
        end_year=scenario.end.year + (scenario.end != date(scenario.end.year, 1, 1)),
        members=[p.model_dump(mode="json") for p in members],
    )
    return payload
