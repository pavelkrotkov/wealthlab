"""Chronological household replacement matching without looking at future trades."""

from datetime import date, timedelta
from decimal import Decimal

from wealthlab.portfolio.wash_basis import adjusted_replacement, loss_amount
from wealthlab.portfolio.wash_keys import key


def eligible(lot, row, used):
    # Only unsold shares remain in book.lots. A shared import lot ID does not
    # exclude retained shares from the same recent acquisition.
    sold = date.fromisoformat(row["date"])
    return (
        lot.id not in used
        and sold - timedelta(days=30) <= lot.acquired <= sold + timedelta(days=30)
        and lot.security_id == row["security_id"]
    )


def match(book, row, used, jurisdiction):
    candidates = sorted(
        list(book.lots.values()), key=lambda lot: (lot.acquired, book.share_order[lot.id])
    )
    for original in candidates:
        if row[key(jurisdiction, "unmatched_quantity")] == 0:
            break
        lot = book.lots.get(original.id)
        if lot is not None and eligible(lot, row, used):
            apply(book, lot, row, used, jurisdiction)


def apply(book, lot, row, used, jurisdiction):
    quantity = min(lot.quantity, row[key(jurisdiction, "unmatched_quantity")])
    amount = loss_amount(row, quantity, jurisdiction)
    replacement, taxable = adjusted_replacement(
        book, lot, quantity, amount, row, used, jurisdiction
    )
    row[key(jurisdiction, "unmatched_quantity")] -= quantity
    row[key(jurisdiction, "disallowed")] += amount
    row[key(jurisdiction, "deferred")] += amount if taxable else Decimal(0)
    row[key(jurisdiction, "permanent")] += Decimal(0) if taxable else amount
    row[key(jurisdiction, "matches")].append(
        dict(
            replacement_lot=replacement,
            account_id=lot.account_id,
            quantity=quantity,
            disallowed=amount,
            basis_increased=taxable,
        )
    )
