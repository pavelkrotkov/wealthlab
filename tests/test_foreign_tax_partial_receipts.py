"""Partial tax payments can use later real cash without reusing an execution identity.

An opening 5,000 and a later actual 5,000 receipt pay the same EUR assessment
in two executions. The unpaid native balance remains debt; retrying without
new cash or after full payment cannot debit the household again.
"""

from datetime import date
from decimal import Decimal

from wealthlab.household.funding import Wallet
from wealthlab.tax.foreign_tax_example import synthetic
from wealthlab.tax.projection_ledger import TaxLedger


def test_partial_payment_then_actual_late_cash_pays_remainder_once_and_retains_schedule_identity():
    scenario = synthetic()
    account = scenario.accounts[0].model_copy(update=dict(balance=Decimal(5000)))
    scenario = scenario.model_copy(update=dict(accounts=[account]))
    ledger, wallet = TaxLedger(scenario.tax_plan, scenario), Wallet(scenario)
    start, end = date(2025, 10, 1), date(2025, 11, 1)

    def late_receipt(wallet, start, end):
        wallet.deposit(Decimal(5000))
        ledger.foreign.retry(ledger, wallet, start, end)
        return []

    row = ledger.month({}, wallet, start, end, Decimal(0), receipt_hook=late_receipt)
    records = row["foreign_tax_cash_records"]
    assert len(records) == len({r["id"] for r in records}) == 2
    assert {r["payment_schedule_id"] for r in records} == {"es_installment"}
    assert row["foreign_tax_paid"] == Decimal(10000)
    assert wallet.cash == 0
    assert row["foreign_tax_positions"][0]["remaining_native"] == Decimal("909.10")
    ledger.foreign.retry(ledger, wallet, start, end)
    assert len(ledger.foreign.payments) == 2


def test_generated_identity_cannot_steal_a_reserved_future_refund_identity_before_cash_debit():
    data = synthetic().model_dump(mode="json")
    from wealthlab.tax.foreign_credit_example import synthetic as credit_example

    original = credit_example().tax_cash[0].model_dump(mode="json")
    original.update(
        id="original_paid",
        value=dict(original["value"], date="2025-09-30", amount="1000"),
        creditable_native="1000",
    )
    observed = dict(assessment_id="es_income_2025", source_income_year=2025, record=original)
    data["foreign_tax_plan"]["opening_payments"] = [observed]
    refund = dict(
        original,
        id="es_installment_2025_10_31",
        kind="refund",
        reverses_id="original_paid",
        value=dict(original["value"], date="2025-11-30", amount="100"),
        creditable_native="100",
    )
    data["foreign_tax_plan"]["refunds"] = [dict(observed, record=refund)]
    from wealthlab.household.scenario import Scenario

    scenario = Scenario.model_validate(data)
    ledger, wallet = TaxLedger(scenario.tax_plan, scenario), Wallet(scenario)
    import pytest

    with pytest.raises(ValueError, match="reserved"):
        ledger.month({}, wallet, date(2025, 10, 1), date(2025, 11, 1), Decimal(0))
    assert wallet.cash == 50000
