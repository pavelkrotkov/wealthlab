"""Household bridges must not silently keep unsupported no-work/death assumptions valid.

Generated cash retains a single source. Annual wages are owner-specific and
include opening YTD amounts; a recipient's retirement date alone proves neither
an earnings-test exemption nor continued household survival/filing treatment.
"""

from datetime import date
from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.household.flows import earning_items
from wealthlab.retirement.social_dates import full_retirement_month
from wealthlab.retirement.social_partnership_earnings import add_wages
from wealthlab.tax.projection_example import age
from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario, result):
    plan = scenario.tax_plan
    if plan is None:
        raise ValueError("Household Social Security requires an explicit annual tax plan.")
    validate_tax(plan, scenario)
    validate_dates(scenario)
    case = scenario.social_security
    members = {p.id: p for p in scenario.members}
    if set(members) != {p.id for p in case.members}:
        raise ValueError("Social Security members must match the household members.")
    for person in case.members:
        validate_person(person, members[person.id], scenario.end)
    validate_ages(scenario)
    validate_sources(scenario)
    validate_work(scenario, result)


def validate_dates(scenario):
    if scenario.start.day != 1 or scenario.end.day != 1:
        raise ValueError("Household Social Security currently requires whole calendar months.")
    case = scenario.social_security
    if date(case.start_year, 1, 1) > scenario.start or date(case.end_year, 1, 1) < scenario.end:
        raise ValueError("The Social Security case must cover the household projection.")


def validate_person(person, member, end):
    if person.birth_date != member.birth_date:
        raise ValueError("Social Security and household birth dates must match.")
    if person.provenance == "unresolved":
        raise ValueError("Resolve Social Security PIAs and eligibility before projecting.")
    if person.death_date is not None and person.death_date < end:
        raise ValueError("Dated deaths require the standalone claim workbench for now.")


def validate_sources(scenario):
    plan = scenario.tax_plan
    if any(r.federal == "social_security" for r in plan.income_rules):
        raise ValueError("Remove manual Social Security income rules when using generated claims.")
    if any(e.federal.social_security for e in plan.events):
        raise ValueError("Remove manual Social Security events when using generated claims.")
    validate_opening(scenario)


def validate_opening(scenario):
    plan = scenario.tax_plan
    opening = next(c for c in plan.cases if c.policy.year == scenario.start.year)
    if scenario.start == date(scenario.start.year, 1, 1) and opening.federal_income.social_security:
        raise ValueError("January opening tax facts must exclude generated Social Security.")


def validate_work(scenario, result):
    if scenario.social_work_plan is not None:
        from wealthlab.retirement.social_work_household_validation import validate

        validate(scenario)
        return
    validate_no_work(scenario, result)


def validate_no_work(scenario, result):
    """Conservative guard until earnings tests and later reduction-factor changes land.

    All annual wages count, including pre-claim wages and opening YTD. Even a
    below-limit positive amount blocks this bridge rather than assuming a grace
    year or exemption. Post-FRA wages remain fully supported by the tax engine.
    """
    fras = {p.id: full_retirement_month(p.birth_date) for p in scenario.social_security.members}
    wages = wage_totals(scenario)
    for row in result["monthly_entitlements"]:
        when, member = row["entitlement_month"], row["member"]
        # Include a pre-start entitlement paid inside the cash horizon. Work
        # deductions still belong to the entitlement year, not the receipt year.
        if not scenario.start <= row["payment_month"] < scenario.end or when >= fras[member]:
            continue
        if row["entitlement_before_offsets"] and wages.get((when.year, member), 0):
            raise ValueError(
                "Pre-FRA benefits with annual wages require the earnings-test layer; "
                "the no-deduction confirmation cannot override changed household wages."
            )


def wage_totals(scenario):
    owners = [p.id for p in scenario.members]
    fields = dict(zip(("wages_primary", "wages_spouse"), owners, strict=False))
    totals = {}
    for case in scenario.tax_plan.cases:
        add_wages(totals, case.policy.year, case.federal_income, fields)
    for event in scenario.tax_plan.events:
        add_wages(totals, event.date.year, event.federal, fields)
    rules = {r.income_id: fields.get(r.federal) for r in scenario.tax_plan.income_rules}
    for start, end in months(scenario.start, scenario.end):
        for identifier, value in earning_items(scenario, start, end).items():
            owner = rules.get(identifier)
            if owner is not None:
                key = start.year, owner
                totals[key] = totals.get(key, Decimal(0)) + value
    return totals


def validate_ages(scenario):
    for annual in scenario.tax_plan.cases:
        if annual.filing.status == "separate":
            raise ValueError(
                "Separate-return Social Security tax treatment is outside this bridge."
            )
        for index, person in enumerate(scenario.members):
            field = ("age_primary", "age_spouse")[index]
            fed = getattr(annual.filing, field)
            nj = getattr(annual.nj_filing or annual.filing, field)
            year = annual.policy.year
            if fed != age(person.birth_date, year, federal=True) or nj != age(
                person.birth_date, year
            ):
                raise ValueError("Annual federal/NJ tax ages must match household birth dates.")
