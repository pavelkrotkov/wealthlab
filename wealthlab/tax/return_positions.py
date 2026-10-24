"""Keep closed-return liabilities separate from actual later tax cash.

A revised return cannot undo a payment or receipt that already happened.
Source-year net payments increase when arrears are paid and decrease when a
refund arrives. Reconciliation can then adjust only the remaining payable or
receivable, rather than paying the same refund twice or forgiving paid debt.
"""

from dataclasses import dataclass
from decimal import Decimal

from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.payments import balances

ZERO = Decimal(0)


@dataclass
class ClosedReturn:
    case: AnnualCase
    result: dict
    net_paid: dict
    received_state_refund: Decimal = ZERO
    taxable_state_received: Decimal = ZERO

    def positions(self):
        due = {j: value - self.net_paid[j] for j, value in liabilities(self.result).items()}
        owed = {j: max(ZERO, value) for j, value in due.items()}
        receivable = {j: max(ZERO, -value) for j, value in due.items()}
        return owed, receivable


def liabilities(result):
    return dict(
        federal=result["federal"]["total"],
        new_jersey=result["new_jersey"]["income_tax"],
    )


def capture(case, result):
    due = balances(result)
    paid = {j: value - due[j] for j, value in liabilities(result).items()}
    return ClosedReturn(case, result, paid)


def record_arrears(ledger, jurisdiction, amount):
    if not amount:
        return
    remaining = amount
    closed = getattr(ledger, "closed_returns", {})
    for year in sorted(closed):
        position = closed[year]
        owed, _ = position.positions()
        paid = min(remaining, owed[jurisdiction])
        position.net_paid[jurisdiction] += paid
        remaining -= paid


def record_refunds(ledger, receipts):
    if hasattr(ledger, "refund_receipts"):
        ledger.refund_receipts.extend(receipts)
    closed = getattr(ledger, "closed_returns", {})
    for receipt in receipts:
        position = closed.get(receipt.get("source_year"))
        if position is None:
            continue
        components = receipt.get("components", {})
        for jurisdiction, amount in components.items():
            position.net_paid[jurisdiction] -= amount
        position.received_state_refund += components.get("new_jersey", ZERO)
        position.taxable_state_received += receipt["taxable"]
