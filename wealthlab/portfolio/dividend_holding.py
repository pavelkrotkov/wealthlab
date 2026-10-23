"""Common-share dividend qualification uses actual risk holding, not wash-tacked basis dates.

Purchase/offset intervals prevent a partial sale or wash split from qualifying the
wrong shares. Acquisition day is excluded and sale day included within the stated
121-day window. Future holding days are provisional; issuer and risk eligibility
must also be confirmed before any qualified amount is recognized."""

from datetime import date, timedelta
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.share_ranges import overlap


def qualifies(acquired, end, ex_date):
    first = max(acquired + timedelta(days=1), ex_date - timedelta(days=60))
    last = min(end, ex_date + timedelta(days=60))
    return (last - first).days + 1 > 60


def portions(book, row, as_of):
    remaining = row["quantity"]
    for sale in book.disposals:
        if sale["purchase_order"] != row["purchase_order"]:
            continue
        sold = date.fromisoformat(sale["date"])
        quantity = overlap(
            row["share_offset"], row["quantity"], sale["share_offset"], sale["quantity"]
        )
        if quantity:
            remaining -= quantity
            yield quantity, min(sold, as_of), True
    if remaining:
        yield remaining, as_of, False


def amounts(book, event, row, as_of):
    if not (
        event.qualified_fraction
        and event.qualified_issuer_confirmed
        and event.undiminished_risk_confirmed
    ):
        return Decimal(0), Decimal(0)
    eligible = pending = Decimal(0)
    for quantity, end, sold in portions(book, row, as_of):
        if qualifies(row["acquired"], end, event.ex_date):
            eligible += quantity
        elif not sold and as_of < event.ex_date + timedelta(days=60):
            pending += quantity
    potential = row["amount"] * event.qualified_fraction
    return (
        money(potential * eligible / row["quantity"]),
        money(potential * pending / row["quantity"]),
    )
