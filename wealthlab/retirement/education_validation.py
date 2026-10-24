"""Reject ambiguous 529 histories, expense reuse and missing cash/tax recipients.

Plan identifiers represent programs, not account portfolios. One shared NJBEST
identifier prevents multiple accounts from multiplying program contribution
room. Limit schedules are supplied assumptions; the first one must already be
in effect on January first. Dates after the case year are never used early.
"""

from datetime import date

from wealthlab.retirement.contribution_assumptions import rule_year
from wealthlab.retirement.education_expenses import validate_allocations, validate_expenses


def validate(case):
    rule_year(case)
    if not case.complete_context:
        raise ValueError(
            "Confirm all relevant program accounts, contributions and expense benefits."
        )
    validate_records(case)
    people, plans, accounts = indexes(case)
    if sum(plan.njbest for plan in case.plans) > 1:
        raise ValueError("Use one shared plan identity for all NJBEST accounts.")
    for plan in case.plans:
        validate_plan(plan, case.year)
    for account in case.accounts:
        validate_account(account, people, plans)
    validate_events(case, accounts)
    validate_expenses(case, people)
    validate_allocations(case, accounts)


def validate_plan(plan, year):
    dates = [limit.effective for limit in plan.limits]
    if len(dates) != len(set(dates)) or min(dates) > date(year, 1, 1):
        raise ValueError("Supply distinct plan-limit dates, including an opening limit.")


def validate_account(account, people, plans):
    if (
        account.owner not in people
        or account.beneficiary not in people
        or account.plan not in plans
    ):
        raise ValueError("Education accounts need known owners, beneficiaries and plans.")


def validate_event_dates(case):
    collections = [case.receipts, case.contributions, case.withdrawals, case.returns]
    for group in collections:
        if any(item.date.year != case.year for item in group):
            raise ValueError("Education cash events must fall in the selected year.")


def validate_events(case, accounts):
    validate_event_dates(case)
    references = [(item.destination, item) for item in case.contributions]
    references += [(item.source, item) for item in case.withdrawals]
    references += [(item.account_id, item) for item in case.returns]
    if any(identity not in accounts for identity, _ in references):
        raise ValueError("Unknown education account in dated event.")


def validate_records(case):
    groups = [
        case.people,
        case.plans,
        case.accounts,
        case.receipts,
        case.contributions,
        case.withdrawals,
        case.returns,
        case.expenses,
        case.allocations,
    ]
    records = [item for group in groups for item in group]
    ids = [item.id for item in records]
    if len(ids) != len(set(ids)) or any(item.provenance == "unresolved" for item in records):
        raise ValueError("Education IDs must be unique and critical assumptions resolved.")


def indexes(case):
    return (
        {item.id: item for item in case.people},
        {item.id: item for item in case.plans},
        {item.id: item for item in case.accounts},
    )
