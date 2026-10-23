"""Chronological household replacement matching without looking at future trades."""

from datetime import date, timedelta
from decimal import Decimal

from wealthlab.portfolio.wash_basis import adjusted_replacement, loss_amount


def eligible(lot, row, book, used):
    sold = date.fromisoformat(row["date"])
    return (
        lot.id not in used
        and lot.id != row["lot_id"]
        and sold - timedelta(days=30) <= lot.acquired <= sold + timedelta(days=30)
        and lot.security_id == row["security_id"]
    )


def match(book, row, used):
    candidates = sorted(list(book.lots.values()), key=lambda lot: lot.acquired)
    for original in candidates:
        if row["wash_unmatched_quantity"] == 0:
            break
        lot = book.lots.get(original.id)
        if lot is not None and eligible(lot, row, book, used):
            apply(book, lot, row, used)


def apply(book, lot, row, used):
    quantity = min(lot.quantity, row["wash_unmatched_quantity"])
    amount = loss_amount(row, quantity)
    replacement, taxable = adjusted_replacement(book, lot, quantity, amount, row, used)
    row["wash_unmatched_quantity"] -= quantity
    row["federal_wash_disallowed"] += amount
    row["federal_wash_deferred"] += amount if taxable else Decimal(0)
    row["federal_wash_permanent"] += Decimal(0) if taxable else amount
    row["wash_matches"].append(
        dict(
            replacement_lot=replacement,
            account_id=lot.account_id,
            quantity=quantity,
            disallowed=amount,
            basis_increased=taxable,
        )
    )
