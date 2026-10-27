"""Contradictory payment evidence cannot manufacture a foreign tax credit."""

import pytest

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_example import synthetic
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("creditable_native", "10001", "Creditable tax cannot exceed"),
        ("income_ids", [], "needs a linked recognized-income source"),
        ("income_ids", ["absent"], "known included-income source"),
        ("reverses_id", "not_a_refund", "Only a tax refund"),
    ],
)
def test_invalid_payment_claims_reject_before_an_annual_credit(field, value, message):
    data = synthetic().model_dump(mode="json")
    data["tax_cash"][0][field] = value
    with pytest.raises(ValueError, match=message):
        evaluate(ForeignCreditCase.model_validate(data))
