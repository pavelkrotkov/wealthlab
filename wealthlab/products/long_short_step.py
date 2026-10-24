"""One observed economic step shared by isolated and actual household ledgers.

Only the caller supplies outside cash. Economic receipts/costs update this
book once; taxes remain separately supplied recognition events. Observation
values never contain a future return used for a present investment decision.
"""

from wealthlab.household.calendar import money
from wealthlab.products.long_short_book import ZERO, equity, gross, snapshot
from wealthlab.products.long_short_margin import check
from wealthlab.products.long_short_returns import apply
from wealthlab.products.long_short_trading import liquidate, rebalance, redeem


def advance(book, case, values, when, month, final):
    entry_cost = money(gross(book) * case.turnover_cost) if month == 0 else ZERO
    entry = check(book, case, values["locked"]) if month == 0 else {}
    row = dict(date=when.isoformat(), opening_equity=equity(book), entry_cost=entry_cost)
    row.update({f"entry_{k}": v for k, v in entry.items()})
    row.update(
        apply(
            book,
            case,
            values["long_return"],
            values["short_return"],
            values["long_yield"],
            values["short_yield"],
        )
    )
    locked = bool(values["locked"] and not book["closed"])
    row.update(locked=locked, **check(book, case, locked))
    row.update(orders(book, case, when, locked))
    if eligible_rebalance(case, month, book, locked):
        row.update(rebalance(book, case))
        row.update({f"post_trade_{k}": v for k, v in check(book, case, locked).items()})
    row.update(terminal(book, case, locked, final))
    row.update(snapshot(book))
    return row


def orders(book, case, when, locked):
    requested = sum((r.amount for r in case.redemptions if r.date == when), ZERO)
    result = dict(redemption_requested=requested, redemption_paid=ZERO, exit_cost=ZERO)
    if requested and not (book["closed"] or locked):
        result.update(redeem(book, requested, case.exit_cost))
    result["redemption_unfilled"] = requested - result["redemption_paid"]
    return result


def eligible_rebalance(case, month, book, locked):
    periods = dict(none=0, monthly=1, quarterly=3, annually=12)
    period = periods[case.rebalance]
    return (
        period and (month + 1) % period == 0 and not (book["closed"] or locked) and equity(book) > 0
    )


def is_locked(book, locks, long, short):
    return bool((book["long"] and locks[long]) or (book["short"] and locks[short]))


def terminal(book, case, locked, final):
    if not (final and case.exit_at_horizon) or book["closed"]:
        return {}
    if locked:
        return dict(terminal_exit_blocked=True)
    return dict(terminal_exit_blocked=False, **liquidate(book, case.exit_cost))
