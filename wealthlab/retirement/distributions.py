"""Fixed IRA cash movements followed by annual tax-basis reconciliation.

Current-year deposits share this cash chronology. Their actual funded basis
enters annual aggregation without financing an earlier unfunded withdrawal.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.retirement import (
    ira_contributions,
    ira_reconciliation,
    rmd,
    roth_reconciliation,
    withdrawal_cash,
)
from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distribution_tax import compare
from wealthlab.retirement.ira_contribution_tax import check as check_contribution_tax


def run(case: DistributionCase):
    book: dict = dict(
        liquidity_locks=case.liquidity_locks,
        accounts={a.id: a for a in case.accounts},
        balances={a.id: a.balance for a in case.accounts},
        cash=case.opening_cash,
        rows=[],
        market_change=Decimal(0),
        rmd=rmd.requirements(case),
    )
    ira_contributions.initialize(case, book)
    balance_events = []
    for when, _, _, item in withdrawal_cash.timeline(case):
        withdrawal_cash.apply(book, item, case)
        balance_events.append(dict(date=when, balances=dict(book["balances"])))
    additions = ira_contributions.summaries(case, book)
    owners = []
    for person in ira_contributions.owners(case, additions):
        traditional = ira_reconciliation.traditional(case, book, person)
        roth = roth_reconciliation.reconcile(case, book, person)
        penalize(book, person)
        owners.append(dict(owner=person.id, **traditional, **roth))
    for entry in book["rmd"].values():
        entry["shortfall"] = max(Decimal(0), entry["required"] - entry["withdrawn"])
    annual = compare(case, book["rows"], additions)
    checked = check_contribution_tax(case, book["rows"], additions, annual)
    return dict(
        year=case.year,
        orders=book["rows"],
        owners=owners,
        cash=book["cash"],
        account_balances=book["balances"],
        balance_events=balance_events,
        market_change=book["market_change"],
        rmd=book["rmd"],
        contribution_orders=book["contribution_rows"],
        contribution_owners=additions,
        contribution_eligibility=checked,
        annual_tax=annual,
    )


def penalize(book, person):
    for row in book["rows"]:
        if row["owner"] != person.id:
            continue
        row["additional_tax"] = Decimal(0)
        exempt = row["early_penalty_exception"] or row["date"] >= roth_reconciliation.half_birthday(
            person.birth_date
        )
        if row["kind"] == "withdrawal" and not exempt:
            base = row["federal_taxable"] + row.get("conversion_recapture", Decimal(0))
            row["additional_tax"] = money(base * Decimal(".10"))
