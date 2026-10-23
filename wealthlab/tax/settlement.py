"""Keep unpaid taxes and delayed refunds as balance-sheet items across year boundaries."""

from datetime import date
from decimal import Decimal

from wealthlab.tax import payments, state_deduction
from wealthlab.tax.annual import evaluate


def close_year(ledger, wallet, start, end) -> dict:
    settled = Decimal(0)
    unfunded = Decimal(0)
    year_end = end >= date(start.year + 1, 1, 1)
    if payments.settlement_due(ledger.plan, start, end):
        ledger.case, settled = payments.settle(
            ledger.case, wallet, ledger.result, ledger.plan.state_deduction_mode
        )
        ledger.result = evaluate(ledger.case)
    if year_end:
        unfunded = finalize(ledger, start)
        current = Decimal(0)
    else:
        current = ledger.result["total_balance"]
    receivable = sum((item["cash"] for item in ledger.refunds), Decimal(0))
    return dict(
        tax_settlement_paid=settled,
        tax_unfunded=unfunded,
        tax_settlement_payment_gap=settlement_gap(ledger, year_end),
        tax_owed=ledger.owed,
        tax_refund_receivable=receivable,
        tax_position=current + ledger.owed - receivable,
        annual_tax=dict(
            ledger.result,
            state_income_tax_deduction_input=ledger.case.federal_deductions.state_local_income_tax_paid,
        ),
        tax_annualized_run_rate=run_rate(ledger.result, start, end),
    )


def finalize(ledger, start):
    due = payments.balances(ledger.result)
    unfunded = sum(max(Decimal(0), value) for value in due.values())
    for jurisdiction, value in due.items():
        ledger.outstanding[jurisdiction] += max(Decimal(0), value)
    refund = sum(max(Decimal(0), -value) for value in due.values())
    taxable, label = state_deduction.recovery(
        ledger.case,
        ledger.result,
        max(Decimal(0), -due["new_jersey"]),
        ledger.plan.state_refund_taxable_fractions,
    )
    ledger.refunds.append(
        dict(
            date=date(start.year + 1, ledger.plan.refund_month, 1),
            cash=refund,
            taxable=taxable,
            treatment=label,
        )
    )
    ledger.result = dict(ledger.result, state_refund_taxable=taxable, state_refund_treatment=label)
    ledger.previous = ledger.result
    return unfunded


def settlement_gap(ledger, year_end):
    if not year_end and ledger.plan.settlement_timing != "monthly_accrued":
        return Decimal(0)
    return sum(max(Decimal(0), value) for value in payments.balances(ledger.result).values())


def run_rate(result: dict, start, end) -> Decimal:
    """Annualize accrued liability for the reserve diagnostic, not future tax law.

    Use calendar-year elapsed time, including opening YTD when starting midyear.
    Refunds do not produce a negative required spending reserve.
    """
    beginning, following = date(start.year, 1, 1), date(start.year + 1, 1, 1)
    elapsed = Decimal((end - beginning).days) / (following - beginning).days
    return max(Decimal(0), result["total_liability"]) / elapsed
