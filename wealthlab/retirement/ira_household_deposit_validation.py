"""Annual eligibility forecasts cannot introduce another household asset pool.

All years and owners need explicit context, even a year with no requests.
The actual IRA opening book is supplied by the household adapter, not a
second user forecast. Reserved receipt IDs prevent a genuine user order
from aliasing an internal funding transfer during annual reconciliation.
"""

from wealthlab.retirement.contribution_inputs import ContributionCase

PREFIX = "household_ira_funding_"


def validate(scenario):
    plan = scenario.ira_plan.contributions
    if not plan.complete_annual_elections_and_context_confirmed:
        raise ValueError("Confirm complete annual IRA elections and eligibility forecasts.")
    if sorted(y.year for y in plan.years) != list(range(scenario.start.year, scenario.end.year)):
        raise ValueError("Provide exactly one IRA contribution context for every household year.")
    validate_events(scenario, plan)
    for year in plan.years:
        validate_year(scenario, year)


def validate_events(scenario, plan):
    records = [*scenario.ira_plan.orders, *scenario.ira_plan.returns, *plan.orders]
    ids = [r.id for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Household IRA events need unique IDs.")
    for record in [*scenario.members, *scenario.accounts, *records]:
        if record.id.startswith(PREFIX):
            raise ValueError("Household IRA IDs cannot use the reserved funding prefix.")
    if any(not scenario.start <= o.date < scenario.end for o in plan.orders):
        raise ValueError("Household IRA deposit orders must lie inside the projection.")


def validate_year(scenario, year):
    validate_people(scenario, year)
    accounts = [a for a in scenario.accounts if a.id in scenario.ira_plan.products]
    orders = [o for o in scenario.ira_plan.contributions.orders if o.date.year == year.year]
    case = annual_case(year, accounts, orders)
    if any(o.kind not in {"traditional_ira", "roth_ira"} for o in case.orders):
        raise ValueError("The ordinary IRA deposit plan cannot fund workplace products.")


def validate_people(scenario, year):
    members = {p.id: p.birth_date for p in scenario.members}
    if {p.id: p.birth_date for p in year.contributors} != members:
        raise ValueError("IRA contributors must match household members and births.")
    annual = next(c for c in scenario.tax_plan.cases if c.policy.year == year.year)
    if year.filing != annual.filing.status:
        raise ValueError("IRA eligibility filing status must match household tax assumptions.")


def annual_case(context, accounts, orders, receipts=()):
    return ContributionCase.model_validate(
        dict(
            **context.model_dump(),
            opening_cash=0,
            accounts=[a.model_dump(exclude={"product"}) for a in accounts],
            orders=orders,
            receipts=list(receipts),
        )
    )
