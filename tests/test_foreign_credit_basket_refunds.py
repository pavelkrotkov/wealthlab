"""Correct refunds retain their original general category; noncredit cash needs no reallocation."""

from decimal import Decimal

import pytest
from foreign_basket_cases import mixed_income

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_example import amount
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


def test_valid_refund_reduces_only_original_general_tax_and_retains_one_cash_receipt():
    data = mixed_income()
    tax = data["tax_cash"][0]
    data["tax_cash"].append(
        dict(
            tax,
            id="refund",
            kind="refund",
            reverses_id=tax["id"],
            value=amount("2025-12-20", 1100),
            creditable_native="1100",
        )
    )
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["observed_tax_cash_outflow_usd"] == 4400
    assert result["candidate"]["federal"]["foreign_tax_credit"] == Decimal("1344.90")
    assert result["carry_audit"]["generated_excess"][0]["amount"] == Decimal("3055.10")
    assert result["carry_audit"]["generated_excess"][0]["basket"] == "general"


@pytest.mark.parametrize("change", ["zero_credit", "wealth_tax", "unknown_basket"])
def test_unclassified_or_noncredit_cash_does_not_invent_a_source_basket(change):
    data = mixed_income()
    tax = data["tax_cash"][0]
    tax["basket"] = "passive"
    if change == "zero_credit":
        tax["creditable_native"] = "0"
    elif change == "wealth_tax":
        tax["tax_type"] = "wealth"
    else:
        tax["basket"] = "unknown"
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["observed_tax_cash_outflow_usd"] == 5500
    if change == "unknown_basket":
        assert result["candidate"] is None
    else:
        assert result["candidate"]["federal"]["foreign_tax_credit"] == 0
