"""Refund cash and original tax-credit reversal use independently dated FX.

The same EUR refund has a different spending value from the original US
credit reversal. A supplied, recognized currency-income row closes that
reconciliation without depositing the refund twice. Unknown ownership and
excess native refunds cannot create another person's tax benefit.
"""

from decimal import Decimal

import pytest

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_example import amount, synthetic
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


def refunded():
    data = synthetic().model_dump(mode="json")
    original = data["tax_cash"][0]
    refund = dict(
        original,
        id="refund",
        kind="refund",
        reverses_id=original["id"],
        value=amount("2025-12-20", 1000, "EUR", "1.40"),
        creditable_native="1000",
    )
    data["tax_cash"].append(refund)
    return data


def test_refund_reverses_original_credit_fx_without_using_that_quote_for_actual_cash():
    result = evaluate(ForeignCreditCase.model_validate(refunded()))
    refund = result["actual_tax_cash"][-1]
    assert refund["observed_cash_outflow_usd"] == Decimal(-1400)
    assert refund["credit_tax_usd"] == Decimal(-1100)
    assert refund["refund_fx_difference_usd"] == Decimal(300)
    assert result["observed_tax_cash_outflow_usd"] == Decimal(9600)
    assert result["candidate"] is None


def test_supplied_currency_income_reconciles_to_observed_fx_without_creating_another_receipt():
    data = refunded()
    data["annual"]["federal_income"]["ordinary_noninvestment_income"] = "300"
    data["income"].append(
        dict(
            id="fx_gain",
            owner_id="person_a",
            country="US",
            kind="ordinary",
            basket="general",
            value=amount("2025-12-20", 300),
            source_classification="Synthetic independently classified noninvestment currency gain",
        )
    )
    data["tax_cash"][-1]["fx_income_id"] = "fx_gain"
    data["fx_income_treatment"] = "included_in_annual_facts"
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["candidate"]["federal"]["agi"] == Decimal(100300)
    assert result["observed_tax_cash_outflow_usd"] == Decimal(9600)
    assert result["basket_audit"][0]["current_tax"] == Decimal(9900)


def test_excess_native_refund_and_a_second_persons_credit_are_rejected():
    data = refunded()
    data["tax_cash"][-1]["value"]["amount"] = "10001"
    with pytest.raises(ValueError, match="Refund cash exceeds"):
        evaluate(ForeignCreditCase.model_validate(data))
    data = synthetic().model_dump(mode="json")
    data["tax_cash"][0]["owner_id"] = "unknown_person"
    with pytest.raises(ValueError, match="known filing-unit person"):
        evaluate(ForeignCreditCase.model_validate(data))
