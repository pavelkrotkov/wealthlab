"""Cash-conserving annual allocation with separate limits, funding and tax basis."""

from datetime import date
from decimal import Decimal

from wealthlab.retirement.contribution_assumptions import rule_year
from wealthlab.retirement.contribution_capacity import allowed
from wealthlab.retirement.contribution_inputs import (
    CashReceipt,
    ContributionCase,
    ContributionOrder,
)
from wealthlab.retirement.contribution_rules import IRA_SOURCE, PLAN_SOURCE
from wealthlab.retirement.ira_rules import deductible

KINDS = ("traditional_ira", "roth_ira", "pretax_401k", "roth_401k")


def run(case: ContributionCase):
    people = {person.id: person for person in case.contributors}
    balances = {account.id: account.balance for account in case.accounts}
    used = {owner: dict.fromkeys(KINDS, Decimal(0)) for owner in people}
    cash, rows = case.opening_cash, []
    for _, _, _, item in timeline(case):
        if isinstance(item, CashReceipt):
            cash += item.amount
            continue
        cap = allowed(case, people[item.owner], item, used[item.owner])
        funded = min(cap, cash)
        cash -= funded
        balances[item.destination] += funded
        used[item.owner][item.kind] += funded
        rows.append(
            dict(
                id=item.id,
                date=item.date.isoformat(),
                owner=item.owner,
                destination=item.destination,
                kind=item.kind,
                requested=item.amount,
                eligible=cap,
                funded=funded,
                blocked_by_limit=item.amount - cap,
                unfunded=cap - funded,
            )
        )
    owners = [summary(case, person, used[person.id]) for person in people.values()]
    return dict(
        year=case.year,
        rule_base_year=rule_year(case),
        rule_mode=case.rule_mode,
        orders=rows,
        owners=owners,
        cash=cash,
        account_balances=balances,
        sources=[
            IRA_SOURCE,
            PLAN_SOURCE,
            "https://www.irs.gov/retirement-plans/plan-participant-employee/"
            "retirement-topics-catch-up-contributions",
            "https://www.nj.gov/treasury/taxation/njit13.shtml",
        ],
    )


def summary(case, person, used):
    deduction = deductible(case, person, used["traditional_ira"])
    return dict(
        owner=person.id,
        **used,
        federal_ira_deduction=deduction,
        new_federal_ira_basis=used["traditional_ira"] - deduction,
        new_nj_ira_basis=used["traditional_ira"],
        new_roth_regular_basis=used["roth_ira"],
        federal_wage_exclusion=used["pretax_401k"],
    )


def timeline(case):
    # Receipts precede orders on the same date; order ties retain supplied order.
    events: list[tuple[date, int, int, CashReceipt | ContributionOrder]] = [
        (item.date, 0, i, item) for i, item in enumerate(case.receipts)
    ]
    events += [(item.date, 1, i, item) for i, item in enumerate(case.orders)]
    return sorted(events, key=lambda event: event[:3])
