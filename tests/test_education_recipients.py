"""A self-funded student is one actual tax recipient, regardless of payment label."""

import pytest

from tests.test_education_cash import calculate, payload


def test_self_beneficiary_is_one_tax_recipient_even_for_different_payees():
    data = payload()
    data["accounts"][0]["owner"] = "student"
    data["allocations"] = [data["allocations"][0]]
    result = calculate(data)
    assert len(result["annual_tax_groups"]) == 1
    assert result["annual_tax_groups"][0]["gross_distribution"] == 20000
    data["allocations"].append(
        {**data["allocations"][0], "id": "duplicate_recipient", "recipient": "beneficiary"}
    )
    with pytest.raises(ValueError, match="actual tax recipient"):
        calculate(data)
