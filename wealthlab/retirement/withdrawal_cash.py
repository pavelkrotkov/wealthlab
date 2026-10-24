"""Move funded amounts exactly once; revaluations are explicit market gains or losses."""

from wealthlab.household.calendar import money
from wealthlab.retirement.distribution_inputs import AccountReturn


def timeline(case):
    events = [(item.date, 0, i, item) for i, item in enumerate(case.returns)]
    events += [(item.date, 1, i, item) for i, item in enumerate(case.orders)]
    return sorted(events, key=lambda event: event[:3])


def apply(book, item):
    if isinstance(item, AccountReturn):
        delta = money(book["balances"][item.account_id] * item.rate)
        book["balances"][item.account_id] += delta
        book["market_change"] += delta
        return
    account = book["accounts"][item.source]
    rmd = book["rmd"][account.owner]
    blocked = item.kind == "conversion" and rmd["withdrawn"] < rmd["required"]
    paid = min(item.amount, book["balances"][item.source]) if not blocked else 0
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
            early_penalty_exception=item.early_penalty_exception,
        )
    )
