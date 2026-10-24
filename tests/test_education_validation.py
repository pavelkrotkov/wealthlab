"""Ambiguous account histories and unsupported wrappers cannot produce a projection."""

import pytest

from tests.test_education_cash import calculate, payload


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("wrapper", "hsa"),
        ("currency", "EUR"),
        ("monthly_fee", 1),
        ("owner", "unknown"),
        ("plan", "unknown"),
        ("provenance", "unresolved"),
    ],
)
def test_invalid_accounts_fail_before_calculation(field, value):
    data = payload()
    data["accounts"][0][field] = value
    with pytest.raises(ValueError):
        calculate(data)


def test_complete_history_must_be_confirmed_and_record_ids_unique():
    data = payload()
    data["complete_context"] = False
    with pytest.raises(ValueError, match="Confirm all relevant"):
        calculate(data)
    data["complete_context"] = True
    data["contributions"][0]["id"] = "college"
    with pytest.raises(ValueError, match="IDs must be unique"):
        calculate(data)


@pytest.mark.parametrize("target", ["contributions", "returns", "withdrawals"])
def test_cash_events_cannot_cross_year_or_reference_missing_accounts(target):
    data = payload()
    data[target][0]["date"] = "2027-01-01"
    with pytest.raises(ValueError, match="selected year"):
        calculate(data)
    data[target][0]["date"] = "2026-01-01"
    field = {"contributions": "destination", "returns": "account_id", "withdrawals": "source"}[
        target
    ]
    data[target][0][field] = "missing"
    with pytest.raises(ValueError, match="Unknown education account"):
        calculate(data)


def test_expense_benefits_and_payment_year_must_reconcile():
    data = payload()
    data["expenses"][0]["paid"] = "2027-01-01"
    with pytest.raises(ValueError, match="selected-year payment"):
        calculate(data)
    data["expenses"][0].update(paid="2026-01-01", tax_free_aid=20000)
    with pytest.raises(ValueError, match="cannot exceed the expense"):
        calculate(data)


def test_nonqualified_expense_cannot_support_an_allocation():
    data = payload()
    data["expenses"][0]["eligibility"] = "not_qualified"
    with pytest.raises(ValueError, match="unavailable"):
        calculate(data)
