"""Allocate each jurisdiction's wash adjustment to exactly the replacement shares matched.

Each jurisdiction adjusts only its own basis; economic cost never changes. Partial
matches split all three bases first, so a later sale of unmatched shares cannot
consume the deferred loss assigned to other shares. IRA basis is not increased.
"""

from datetime import date

from wealthlab.household.calendar import money
from wealthlab.portfolio.lot_parts import split
from wealthlab.portfolio.wash_keys import key


def adjusted_replacement(book, lot, quantity, amount, loss, used, jurisdiction):
    """Split partial matches; untouched shares keep their own basis and holding start."""
    matched = split_replacement(book, lot, quantity)
    taxable = book.accounts[lot.account_id].wrapper == "taxable"
    if taxable:
        updates = {jurisdiction + "_basis": getattr(matched, jurisdiction + "_basis") + amount}
        if jurisdiction == "federal":
            updates["federal_holding_start"] = holding_start(lot, loss)
        matched = matched.model_copy(update=updates)
    book.lots[matched.id] = matched
    used.add(matched.id)
    return matched.id, taxable


def holding_start(lot, loss):
    start = date.fromisoformat(loss["federal_holding_start"])
    sold = date.fromisoformat(loss["date"])
    prior_days = max(0, (min(sold, lot.acquired) - start).days)
    return date.fromordinal(lot.acquired.toordinal() - prior_days)


def split_replacement(book, lot, quantity):
    """Economic cost and both tax bases split independently before any tax adjustment."""
    matched, remaining = split(lot, quantity)
    if remaining.quantity:
        matched_id = unique_id(book, lot.id)
        matched = matched.model_copy(update={"id": matched_id})
        book.origins[matched_id] = book.origins[lot.id]
        order, offset = book.share_order[lot.id]
        book.share_order[matched_id] = (order, offset)
        book.share_order[lot.id] = (order, offset + quantity)
        book.lots[lot.id] = remaining
        for ledger in (book.wash, book.nj_wash):
            if lot.id in ledger.used:
                ledger.used.add(matched_id)
    return matched


def unique_id(book, original):
    prefix = original[:60] + "_wash_"
    index = 1
    while prefix + str(index) in book.allocated_ids:
        index += 1
    identity = prefix + str(index)
    book.allocated_ids.add(identity)
    return identity


def loss_amount(row, quantity, jurisdiction):
    """Allocate the final cent to the last matched shares, preserving the total loss."""
    remaining = -row[jurisdiction + "_gross_gain"] - row[key(jurisdiction, "disallowed")]
    if quantity == row[key(jurisdiction, "unmatched_quantity")]:
        return remaining
    return min(remaining, money(-row[jurisdiction + "_gross_gain"] * quantity / row["quantity"]))
