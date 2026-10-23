"""Keep unpaid taxes and delayed refunds as balance-sheet items across year boundaries."""

from datetime import date
from decimal import Decimal

from wealthlab.tax import payments


def close_year(ledger, wallet, start, end) -> dict:
    settled = Decimal(0)
    unfunded = Decimal(0)
    if end >= date(start.year + 1, 1, 1):
        ledger.case, settled = payments.settle(ledger.case, wallet, ledger.result)
        ledger.result = reconcile(ledger.result, ledger.case)
        due = payments.balances(ledger.result)
        unfunded = sum(max(Decimal(0), value) for value in due.values())
        ledger.owed += unfunded
        refund = sum(max(Decimal(0), -value) for value in due.values())
        ledger.refunds.append((date(start.year + 1, ledger.plan.refund_month, 1), refund))
        ledger.previous = ledger.result
        current = Decimal(0)
    else:
        current = ledger.result["total_balance"]
    receivable = sum((value for _, value in ledger.refunds), Decimal(0))
    return dict(
        tax_settlement_paid=settled,
        tax_unfunded=unfunded,
        tax_owed=ledger.owed,
        tax_refund_receivable=receivable,
        tax_position=current + ledger.owed - receivable,
        annual_tax=ledger.result,
        tax_annualized_run_rate=run_rate(ledger.result, start, end),
    )


def reconcile(result: dict, case) -> dict:
    """Cash payments change balances only; avoid rerunning the numerical tax engine."""
    paid = case.payments
    fed = result["federal"]["income_tax"] - paid.federal_income_withheld - paid.federal_estimates
    payroll = result["federal"]["employee_payroll"] - paid.employee_payroll_withheld
    nj = result["new_jersey"]["income_tax"] - paid.nj_withheld - paid.nj_estimates
    return dict(
        result,
        federal_income_balance=fed,
        payroll_balance=payroll,
        nj_balance=nj,
        total_balance=fed + payroll + nj,
    )


def run_rate(result: dict, start, end) -> Decimal:
    """Annualize accrued liability for the reserve diagnostic, not future tax law.

    Use calendar-year elapsed time, including opening YTD when starting midyear.
    Refunds do not produce a negative required spending reserve.
    """
    beginning, following = date(start.year, 1, 1), date(start.year + 1, 1, 1)
    elapsed = Decimal((end - beginning).days) / (following - beginning).days
    return max(Decimal(0), result["total_liability"]) / elapsed
