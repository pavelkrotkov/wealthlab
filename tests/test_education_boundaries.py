"""Fail closed on missing programs, expense identities and unsupported opening history."""

import pytest

from tests.test_education_cash import calculate, payload


@pytest.mark.parametrize("missing", ["account", "expense"])
def test_unknown_allocation_reference_is_rejected(missing):
    data = payload()
    if missing == "account":
        data["allocations"][0]["account"] = "missing"
    else:
        data["allocations"][0]["expenses"][0]["expense"] = "missing"
    with pytest.raises(ValueError, match="Unknown education"):
        calculate(data)


def test_allocation_without_a_withdrawal_is_not_a_hypothetical_tax_saving():
    data = payload()
    data["withdrawals"] = []
    with pytest.raises(ValueError, match="requires a withdrawal"):
        calculate(data)


@pytest.mark.parametrize("dates", [["2026-01-02"], ["2025-01-01", "2025-01-01"]])
def test_plan_needs_one_unambiguous_opening_limit(dates):
    data = payload()
    data["plans"][0]["limits"] = [dict(effective=day, maximum_balance=305000) for day in dates]
    with pytest.raises(ValueError, match="opening limit"):
        calculate(data)


def test_two_njbest_labels_cannot_multiply_program_contribution_capacity():
    data = payload()
    data["plans"].append({**data["plans"][0], "id": "duplicate_program"})
    with pytest.raises(ValueError, match="one shared plan identity"):
        calculate(data)


def test_empty_opening_account_cannot_preserve_an_already_closed_loss():
    data = payload()
    data["accounts"][0]["balance"] = 0
    with pytest.raises(ValueError, match="closed-account basis"):
        calculate(data)
