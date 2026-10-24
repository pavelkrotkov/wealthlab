"""Bad opening context and receipt links fail before funding mutates balances."""

import pytest
from test_hsa_cash import calculate, payload


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("receipt_ids", ["missing"], "known and unique"),
        ("receipt_ids", ["medical", "medical"], "known and unique"),
        ("source", "missing", "Unknown HSA"),
        ("date", "2027-01-01", "selected year"),
        ("provenance", "unresolved", "Resolve critical"),
    ],
)
def test_invalid_withdrawal_blocks_case(field, value, message):
    data = payload()
    data["withdrawals"][0][field] = value
    with pytest.raises(ValueError, match=message):
        calculate(data)


def test_prior_receipt_claims_cannot_exceed_paid_expense():
    data = payload()
    data["medical_receipts"][0]["deducted_federally"] = "2500.00"
    with pytest.raises(ValueError, match="exceed the receipt"):
        calculate(data)


def test_coverage_calendar_requires_twelve_distinct_months():
    data = payload()
    data["owners"][0]["months"][0]["month"] = 2
    with pytest.raises(ValueError, match="twelve distinct"):
        calculate(data)


def test_opening_context_confirmation_is_required():
    data = payload()
    data["complete_context"] = False
    with pytest.raises(ValueError, match="Confirm complete HSA"):
        calculate(data)
