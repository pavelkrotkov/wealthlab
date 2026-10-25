"""Report domestic cash separately from the one shared foreign-tax cash book."""

from decimal import Decimal

from wealthlab.tax import foreign_tax_household, payments, recognition, required_funding
from wealthlab.tax.annual import evaluate


def report(
    ledger, amounts, start, end, paid, estimates, prior_paid, received, taxable_refund, event_cash
):
    foreign = foreign_tax_household.completed(ledger, start, end)
    return dict(
        social_security_cash=recognition.social_cash(amounts, ledger.plan.income_rules),
        tax_withheld=paid - estimates,
        tax_estimates_paid=estimates,
        tax_payment_gap=max(Decimal(0), sum(ledger.month_requested.values()) - paid),
        prior_tax_paid=prior_paid,
        funding_sale_proceeds=required_funding.finish(ledger),
        tax_refund_received=received,
        taxable_state_refund=taxable_refund,
        tax_event_cash=event_cash,
        tax_source_withholding=sum(
            (r["federal_income_withheld"] + r["nj_withheld"] for r in ledger.source_receipts),
            Decimal(0),
        ),
        tax_source_receipts=list(ledger.source_receipts),
        **foreign,
    )


def pay_current(ledger, wallet, amounts, start, end):
    result = evaluate(ledger.case)
    requested = payments.ledger_request(ledger, amounts, result, start, end)
    ledger.month_requested = requested
    before = ledger.case.payments
    ledger.case, paid = payments.pay(
        ledger.case, wallet, requested, ledger.plan.state_deduction_mode
    )
    estimates = (
        ledger.case.payments.federal_estimates
        - before.federal_estimates
        + ledger.case.payments.nj_estimates
        - before.nj_estimates
    )
    ledger.result = evaluate(ledger.case)
    return paid, estimates
