"""Move funded amounts exactly once; revaluations are explicit market gains or losses."""

from wealthlab.household.calendar import money
from wealthlab.retirement.account_liquidity import blocked as liquidity_blocked
from wealthlab.retirement.contribution_inputs import CashReceipt, ContributionOrder
from wealthlab.retirement.distribution_inputs import AccountReturn
from wealthlab.retirement.ira_contributions import fund


def timeline(case):
    # Same-day receipts, returns, withdrawals/conversions, then contributions.
    events = [(item.date, 1, i, item) for i, item in enumerate(case.returns)]
    events += [(item.date, 2, i, item) for i, item in enumerate(case.orders)]
    if case.contributions is not None:
        events += [(item.date, 0, i, item) for i, item in enumerate(case.contributions.receipts)]
        events += [(item.date, 3, i, item) for i, item in enumerate(case.contributions.orders)]
    return sorted(events, key=lambda event: event[:3])


def apply(book, item, case=None):
    if isinstance(item, CashReceipt):
        book["cash"] += item.amount
        return
    if isinstance(item, ContributionOrder):
        fund(case, book, item)
        return
    if isinstance(item, AccountReturn):
        delta = money(book["balances"][item.account_id] * item.rate)
        book["balances"][item.account_id] += delta
        book["market_change"] += delta
        return
    withdraw(book, item)


def withdraw(book, item):
    account = book["accounts"][item.source]
    rmd = book["rmd"][account.owner]
    blocked = item.kind == "conversion" and rmd["withdrawn"] < rmd["required"]
    locked = liquidity_blocked(book["liquidity_locks"], item.source, item.date)
    paid = min(item.amount, book["balances"][item.source]) if not (blocked or locked) else 0
    book["balances"][item.source] -= paid
    if item.kind == "conversion":
        book["balances"][item.destination] += paid
    else:
        book["cash"] += paid
        if account.wrapper == "traditional":
            rmd["withdrawn"] += paid
    book["rows"].append(
        dict(
            id=item.id,
            date=item.date,
            owner=account.owner,
            source=item.source,
            destination=item.destination,
            kind=item.kind,
            wrapper=account.wrapper,
            requested=item.amount,
            paid=paid,
            unfilled=item.amount - paid,
            blocked_by_rmd=bool(blocked),
            blocked_by_liquidity=locked,
            early_penalty_exception=item.early_penalty_exception,
        )
    )
