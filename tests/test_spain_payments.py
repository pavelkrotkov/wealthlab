"""Refund credit reversals retain original recognized tax while cash uses receipt FX."""

from decimal import Decimal

import pytest
from spain_cases import payment

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import amount, synthetic
from wealthlab.tax.spain_inputs import SpainCase


def refunded():
    original = payment(100)
    original["value"] = amount(125, "2026-06-20", "USD", ".8")
    refund = payment(40, "refund", "refund", "paid")
    refund["value"] = amount(50, "2026-07-01", "USD", "1.1")
    data = synthetic().model_dump(mode="json")
    data["payments"] = [original, refund]
    return data


def test_refund_cash_fx_does_not_change_the_supplied_original_tax_credit_reversal():
    case = SpainCase.model_validate(refunded())
    result = evaluate(case)
    assert result["wealth"]["assessment"]["wealth_actually_paid"] == 60
    assert case.payments[0].value.euros() == 100
    assert case.payments[1].value.euros() == 55
    assert result["recognized_payments_eur"]["wealth"] == Decimal(60)


@pytest.mark.parametrize(
    "index,field,value,match",
    [
        (0, "liability_year", 2026, "liability year"),
        (0, "reverses_id", "refund", "Only a refund"),
        (1, "reverses_id", "absent", "original payment"),
        (1, "reverses_id", "refund", "original payment"),
        (1, "tax_type", "irpf", "same tax type"),
        (1, "recognized_tax_eur", "101", "more recognized tax"),
    ],
)
def test_invalid_observed_tax_payment_identity_or_refund_is_rejected(index, field, value, match):
    data = refunded()
    data["payments"][index][field] = value
    with pytest.raises(ValueError, match=match):
        SpainCase.model_validate(data)


@pytest.mark.parametrize("when", ["2027-01-01", "2026-01-01"])
def test_a_refund_cannot_precede_its_payment_or_follow_the_observation_date(when):
    data = refunded()
    data["payments"][1]["value"]["date"] = when
    with pytest.raises(ValueError):
        SpainCase.model_validate(data)


def test_ip_overpayment_is_not_turned_into_an_unlimited_solidarity_credit():
    data = synthetic().model_dump(mode="json")
    data["payments"] = [payment(30000)]
    with pytest.raises(ValueError, match="overpayment adapter"):
        evaluate(SpainCase.model_validate(data))
