"""Every dated recognition route credits payer tax without another cash draw.

Four independent $10,000 gross pension payments produce $32,000 net cash,
not $40,000 spendable cash. The $8,000 difference remains paid tax. A new
month resets only the audit totals; annual payment credits remain carried.
"""

from datetime import date
from decimal import Decimal

from wealthlab.household.funding import Wallet
from wealthlab.tax.projection_ledger import TaxLedger
from wealthlab.tax.source_example import pension, synthetic


def test_plan_extra_and_both_receipt_hooks_share_source_credit_accounting():
    scenario = synthetic()
    ledger = TaxLedger(scenario.tax_plan, scenario)
    wallet = Wallet(scenario)
    start, end = date(2026, 2, 1), date(2026, 3, 1)

    def hook(*_):
        return [pension()]

    row = ledger.month({}, wallet, start, end, Decimal(0), [pension()], hook, hook)
    assert row["tax_event_cash"] == wallet.cash == 32000
    assert row["tax_source_withholding"] == 8000
    assert len(row["tax_source_receipts"]) == 4
    assert ledger.case.payments.federal_income_withheld == 8000
    following = ledger.month({}, wallet, end, date(2026, 4, 1), Decimal(0))
    assert following["tax_source_withholding"] == 0
    assert following["tax_source_receipts"] == []
    assert ledger.case.payments.federal_income_withheld == 8000


def test_nj_source_payment_deduction_is_not_added_again_on_year_boundary():
    scenario = synthetic()
    data = pension().model_dump(mode="json")
    data["withholding"]["nj_withheld"] = 300
    data["cash_received"] = 7700
    item = type(pension()).model_validate(data)
    taxes = scenario.tax_plan.model_copy(update=dict(events=[item]))
    from wealthlab.household.projection import project

    rows = project(scenario.model_copy(update=dict(tax_plan=taxes)))
    assert rows[11]["annual_tax"]["state_income_tax_deduction_input"] == 300
    assert rows[12]["annual_tax"]["state_income_tax_deduction_input"] == 0
    assert rows[15]["tax_refund_received"] == 2300
    assert sum(r["tax_source_withholding"] for r in rows) == 2300
