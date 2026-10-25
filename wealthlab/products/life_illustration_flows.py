"""Loans create cash and equal debt; capitalized interest is a noncash liability.

Embedded policy charges already affect supplied values and must not be entered
again as external fees. Dated cash dividends are receipts; paid-up additions or
retained dividends stay inside the supplied value, not an extra cash receipt.
"""

from decimal import Decimal

ZERO = Decimal(0)
INFLOWS = {"dividend_cash", "withdrawal", "loan_advance"}
OUTFLOWS = {"premium", "loan_principal_repayment", "loan_interest_payment", "external_fee"}


def cash(flow):
    if flow.kind in INFLOWS:
        return flow.amount
    return -flow.amount if flow.kind in OUTFLOWS else ZERO


def debt(flows):
    balance = ZERO
    for flow in flows:
        if flow.kind in {"loan_advance", "capitalized_interest"}:
            balance += flow.amount
        elif flow.kind == "loan_principal_repayment":
            balance -= flow.amount
        if balance < 0:
            raise ValueError("Loan principal repayments exceed the supplied outstanding debt.")
    return balance


def totals(flows):
    return {
        kind: sum((f.amount for f in flows if f.kind == kind), ZERO)
        for kind in (*sorted(INFLOWS), *sorted(OUTFLOWS), "capitalized_interest")
    }
