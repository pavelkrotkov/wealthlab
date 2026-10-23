"""Allocate a federal wash adjustment to exactly the replacement shares matched.

NJ basis and economic cost do not inherit this federal adjustment. Partial
matches split all three bases first, so a later sale of unmatched shares cannot
consume the deferred loss assigned to other shares. IRA basis is not increased.
"""

from datetime import date

from wealthlab.household.calendar import money
from wealthlab.portfolio.lot_parts import split


def adjusted_replacement(book, lot, quantity, amount, loss, used):
    """Split partial matches; untouched shares keep their own basis and holding start."""
    matched = split_replacement(book, lot, quantity)
    taxable = book.accounts[lot.account_id].wrapper == "taxable"
    if taxable:
        start = date.fromisoformat(loss["federal_holding_start"])
        sold = date.fromisoformat(loss["date"])
        prior_days = max(0, (min(sold, lot.acquired) - start).days)
        matched = matched.model_copy(
            update=dict(
                federal_basis=matched.federal_basis + amount,
                federal_holding_start=date.fromordinal(lot.acquired.toordinal() - prior_days),
            )
        )
    book.lots[matched.id] = matched
    used.add(matched.id)
    return matched.id, taxable


def split_replacement(book, lot, quantity):
    """Economic cost and both tax bases split independently before any tax adjustment."""
    matched, remaining = split(lot, quantity)
    if remaining.quantity:
        matched_id = unique_id(book, lot.id)
        matched = matched.model_copy(update={"id": matched_id})
        book.origins[matched_id] = book.origins[lot.id]
        book.lots[lot.id] = remaining
    return matched


def unique_id(book, original):
    prefix = original[:60] + "_wash_"
    index = 1
    while prefix + str(index) in book.lots:
        index += 1
    return prefix + str(index)


def loss_amount(row, quantity):
    """Allocate the final cent to the last matched shares, preserving the total loss."""
    remaining = -row["federal_gross_gain"] - row["federal_wash_disallowed"]
    if quantity == row["wash_unmatched_quantity"]:
        return remaining
    return min(remaining, money(-row["federal_gross_gain"] * quantity / row["quantity"]))
