"""Reject duplicated wage exclusions and ambiguous product classifications.

Annual eligibility forecasts limit elections but cannot manufacture current
payroll cash. Every year must be supplied, including a year with no orders.
The household employment adapter runs first, so job-loss months use its
actual generated gross wage streams rather than the eligibility forecast.

Complete calendar years exclude unknown opening elective deferrals. All
current employee elections belong in this plan; separate payroll/manual tax
inputs would otherwise consume room or exclude the same wages twice.
"""

from wealthlab.retirement.contribution_assumptions import rule_year
from wealthlab.retirement.contribution_validation import validate_order
from wealthlab.retirement.workplace_products import validate_products
from wealthlab.retirement.workplace_wages import validate_wages
from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario):
    plan = scenario.workplace_plan
    if scenario.tax_plan is None:
        raise ValueError("Employee deferrals require household tax assumptions.")
    validate_tax(scenario.tax_plan, scenario)
    if not (
        plan.complete_single_employer_elections_confirmed
        and plan.gross_wages_before_deferrals_confirmed
    ):
        raise ValueError("Confirm complete single-employer elections and gross pre-deferral wages.")
    if (scenario.start.month, scenario.start.day, scenario.end.month, scenario.end.day) != (
        1,
        1,
        1,
        1,
    ):
        raise ValueError("Employee deferrals require complete calendar years.")
    years = [y.year for y in plan.years]
    if sorted(years) != list(range(scenario.start.year, scenario.end.year)):
        raise ValueError("Provide exactly one employee-deferral context for every calendar year.")
    validate_products(scenario)
    validate_years(scenario)
    validate_wages(scenario)


def validate_years(scenario):
    plan = scenario.workplace_plan
    accounts = {a.id: a for a in scenario.accounts}
    members = {m.id: m.birth_date for m in scenario.members}
    ids = [o.id for o in plan.orders]
    if len(ids) != len(set(ids)):
        raise ValueError("Employee deferral order IDs must be unique.")
    if any(not scenario.start <= o.date < scenario.end for o in plan.orders):
        raise ValueError("Employee elections must fall inside the projection.")
    for year in plan.years:
        validate_year(year, plan, accounts, members)


def validate_year(year, plan, accounts, members):
    rule_year(year)
    people = {p.id: p for p in year.contributors}
    if (
        len(people) != len(year.contributors)
        or {p.id: p.birth_date for p in people.values()} != members
    ):
        raise ValueError("Employee contributors must match household IDs and birth dates.")
    if any(p.provenance == "unresolved" for p in people.values()):
        raise ValueError("Resolve employee eligibility assumptions.")
    validate_orders(year, plan, accounts, people)


def validate_orders(year, plan, accounts, people):
    for order in [o for o in plan.orders if o.date.year == year.year]:
        validate_order(order, people, accounts)
        if order.provenance == "unresolved" or plan.products.get(order.destination) != order.kind:
            raise ValueError("Resolve employee order assumptions and match account products.")
