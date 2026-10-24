"""Freeze ex-date entitlements before trades; later cash receipts do not recheck ownership.

Cash is rounded cumulatively within each account so splitting one holding into
many small lots cannot create extra cents or negative final allocations. Payment
only converts a receivable to cash; existing unpaid fees retain payment priority."""

from collections import defaultdict
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.fees import settle


def entitle(book, event):
    accounts = defaultdict(list)
    for lot in book.lots.values():
        if lot.security_id == event.security_id and lot.acquired < event.ex_date:
            accounts[lot.account_id].append(lot)
    for account, lots in accounts.items():
        cumulative = paid = Decimal(0)
        for lot in lots:
            cumulative += lot.quantity * event.per_share
            amount = money(cumulative) - paid
            paid += amount
            order, offset = book.share_order[lot.id]
            book.distributions.append(
                dict(
                    distribution=event.id,
                    account_id=account,
                    security_id=event.security_id,
                    lot_id=lot.id,
                    acquired=lot.acquired,
                    purchase_order=order,
                    share_offset=offset,
                    quantity=lot.quantity,
                    amount=amount,
                    paid=False,
                    recognized=False,
                )
            )


def pay(book, event):
    for row in book.distributions:
        if row["distribution"] == event.id and not row["paid"]:
            book.cash[row["account_id"]] += row["amount"]
            row["paid"] = True
    for account in book.accounts:
        settle(book, account)


def recognize(book, event):
    for row in book.distributions:
        if row["distribution"] == event.id:
            row["recognized"] = True


def receivable(book):
    return sum((row["amount"] for row in book.distributions if not row["paid"]), Decimal(0))
