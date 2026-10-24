"""Refuse unsupported opening history and ambiguous ownership before funding."""

from datetime import date

from wealthlab.retirement.contribution_assumptions import rule_year


def validate(case):
    rule_year(case)
    people = {item.id: item for item in case.contributors}
    accounts = {item.id: item for item in case.accounts}
    validate_records(case)
    validate_people(case)
    validate_budgets(case)
    for account in accounts.values():
        if account.owner not in people or account.currency != "USD" or account.monthly_fee:
            raise ValueError("Use known owners and USD accounts without monthly fees here.")
    validate_events(case, people, accounts)
    validate_destinations(case)


def validate_records(case):
    """IDs span all tables so exported orders cannot alias their owner/account.

    Provenance is checked before any mutation; unresolved eligibility is never
    interpreted as permission to fund a tax-advantaged account.
    """
    records = [*case.contributors, *case.accounts, *case.receipts, *case.orders]
    ids = [item.id for item in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Contribution case IDs must be unique across all tables.")
    if any(item.provenance == "unresolved" for item in records):
        raise ValueError("Resolve contribution assumptions before calculating.")


def validate_people(case):
    expected = 2 if case.filing == "joint" else 1
    if len(case.contributors) != expected:
        raise ValueError("List both joint-filing contributors, or one for other filing statuses.")
    if case.filing != "separate" and case.spouse_covered_by_workplace_plan:
        raise ValueError("Separate-filer spouse coverage is only used for separate returns.")
    if any(item.birth_date > date(case.year, 1, 1) for item in case.contributors):
        raise ValueError("Birth dates must precede the contribution year.")


def validate_budgets(case):
    """Joint compensation is an annual shared resource, allocated explicitly.

    Fixed budgets avoid reallocating a spouse's compensation based on future
    funding failures. Unused capacity stays visible rather than being invented.
    Individual filers cannot borrow another person's eligible compensation.
    """
    people = case.contributors
    if case.filing == "joint":
        if sum(p.ira_compensation_budget for p in people) > sum(
            p.eligible_ira_compensation for p in people
        ):
            raise ValueError("Joint IRA budgets exceed combined eligible compensation.")
    elif people[0].ira_compensation_budget > people[0].eligible_ira_compensation:
        raise ValueError("IRA budget exceeds the owner's eligible compensation.")


def validate_events(case, people, accounts):
    for item in [*case.receipts, *case.orders]:
        if item.date.year != case.year:
            raise ValueError("Cash events must fall within the selected contribution year.")
    for order in case.orders:
        validate_order(order, people, accounts)


def validate_order(order, people, accounts):
    account = accounts.get(order.destination)
    if order.owner not in people or account is None or account.owner != order.owner:
        raise ValueError("Contribution destination must belong to its contributing owner.")
    wrapper = "roth" if order.kind.startswith("roth") else "traditional"
    if account.wrapper != wrapper:
        raise ValueError("Contribution kind disagrees with destination wrapper.")


def validate_destinations(case):
    """A wrapper alone does not make an IRA interchangeable with a 401(k).

    Keep account identity distinct so later withdrawal and rollover rules can
    recover the correct source product instead of guessing from its balance.
    """
    kinds = {}
    for item in case.orders:
        previous = kinds.setdefault(item.destination, item.kind)
        if previous != item.kind:
            raise ValueError("Separate IRA and workplace contributions into distinct accounts.")
