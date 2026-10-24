"""Reject incomplete 529 inventories, duplicate tuition and duplicate NJ deductions.

Every household education account shares a single terms inventory and actual
wallet balance. Owners must belong to the filing unit, so a funded deposit
cannot accidentally claim another taxpayer's NJBEST deduction. Tuition bills
are separately confirmed net eligible costs: they cannot also appear in the
ordinary household education budget or another credit/vehicle allocation.
The annual engine still validates plan identities, recipients and shared caps.
"""

from wealthlab.retirement.education_household_case import annual_case
from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario):
    plan = scenario.education_plan
    if scenario.tax_plan is None:
        raise ValueError("Household education funding requires explicit household taxes.")
    validate_tax(scenario.tax_plan, scenario)
    if not all(
        (
            plan.complete_context_confirmed,
            plan.qualified_net_expenses_separate_from_other_budgets_confirmed,
            plan.contributions_belong_to_filing_unit_confirmed,
        )
    ):
        raise ValueError(
            "Confirm complete 529 context, separate net tuition and filing-unit deposits."
        )
    if (scenario.start.month, scenario.start.day, scenario.end.month, scenario.end.day) != (
        1,
        1,
        1,
        1,
    ):
        raise ValueError("Household education funding requires complete calendar years.")
    validate_accounts(scenario)
    validate_events(scenario)
    validate_event_accounts(scenario)
    validate_deductions(scenario)
    for year in range(scenario.start.year, scenario.end.year):
        annual_case(scenario, year)


def validate_accounts(scenario):
    plan = scenario.education_plan
    accounts = {a.id for a in scenario.accounts if a.wrapper == "education"}
    terms = [a.account_id for a in plan.accounts]
    if not accounts or len(terms) != len(set(terms)) or set(terms) != accounts:
        raise ValueError("Supply exactly one set of terms for every household 529 account.")
    validate_owners_and_transfers(scenario, accounts)


def validate_owners_and_transfers(scenario, accounts):
    members = {p.id for p in scenario.members}
    for account in scenario.accounts:
        if account.id in accounts and account.owner not in members:
            raise ValueError("Household 529 owners must belong to the filing unit.")
    if any(c.destination in accounts for c in scenario.contributions):
        raise ValueError("Remove generic contributions into modeled 529 accounts.")


def validate_events(scenario):
    plan = scenario.education_plan
    records = [*plan.contributions, *plan.tuition, *plan.returns]
    if any(not scenario.start <= r.date < scenario.end for r in records):
        raise ValueError("Household education events must lie inside the projection.")
    if len({r.id for r in records}) != len(records):
        raise ValueError("Household education event IDs must be unique across years.")


def validate_deductions(scenario):
    if any(c.nj_deductions.njbest for c in scenario.tax_plan.cases) or any(
        e.njbest_contributions for e in scenario.tax_plan.events
    ):
        raise ValueError("Remove manual NJBEST deductions when generating actual 529 deposits.")


def validate_event_accounts(scenario):
    plan = scenario.education_plan
    accounts = {a.account_id for a in plan.accounts}
    references = [r.destination for r in plan.contributions]
    references += [r.source for r in plan.tuition]
    references += [r.account_id for r in plan.returns]
    if set(references) - accounts:
        raise ValueError("Unknown household 529 account in dated event.")
