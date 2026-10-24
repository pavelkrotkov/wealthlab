"""Consume each qualified receipt once across every configured household HSA."""

from decimal import Decimal


def available(receipt, owner, when, remaining):
    valid = (
        receipt.eligibility == "qualified_medical"
        and owner.id in receipt.eligible_owners
        and owner.established is not None
        and receipt.incurred >= owner.established
        and receipt.paid <= when
    )
    return remaining[receipt.id] if valid else Decimal(0)


def capacity(book, order, owner):
    return sum(
        (
            available(book["receipts"][key], owner, order.date, book["receipt_remaining"])
            for key in order.receipt_ids
        ),
        Decimal(0),
    )


def consume(book, order, owner, amount):
    used = Decimal(0)
    for key in order.receipt_ids:
        receipt = book["receipts"][key]
        paid = min(amount - used, available(receipt, owner, order.date, book["receipt_remaining"]))
        book["receipt_remaining"][key] -= paid
        used += paid
    return used


def validate_receipt(receipt, owners):
    if set(receipt.eligible_owners) - owners.keys() or receipt.eligibility == "unresolved":
        raise ValueError("Confirm medical eligibility and all eligible HSA receipt owners.")
    if receipt.reimbursed_elsewhere + receipt.deducted_federally > receipt.amount:
        raise ValueError("Prior reimbursement and federal deductions exceed the receipt amount.")
    if receipt.paid < receipt.incurred:
        raise ValueError("This receipt model excludes advance payments before medical care.")
