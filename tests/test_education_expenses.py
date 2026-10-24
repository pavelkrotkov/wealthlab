"""Shared expense reservations cannot be reused by another account, person or tax benefit."""

import pytest

from tests.test_education_cash import calculate, payload


def test_unused_credit_aid_and_other_vehicle_reservations_are_not_529_expenses():
    data = payload()
    data["allocations"][1]["expenses"][0]["amount"] = 2001
    with pytest.raises(ValueError, match="reused or unavailable"):
        calculate(data)


def test_second_account_cannot_reuse_the_first_accounts_expense():
    data = payload()
    data["accounts"].append({**data["accounts"][0], "id": "other"})
    data["allocations"].append({**data["allocations"][0], "id": "reuse", "account": "other"})
    with pytest.raises(ValueError, match="reused or unavailable"):
        calculate(data)


def test_different_beneficiary_cannot_claim_the_students_expenses():
    data = payload()
    data["accounts"][0]["beneficiary"] = "parent"
    data["allocations"] = [data["allocations"][0]]
    with pytest.raises(ValueError, match="another beneficiary"):
        calculate(data)


def test_later_same_year_expense_qualifies_without_changing_prior_funding():
    data = payload()
    data["expenses"][0].update(
        amount=20000, tax_free_aid=0, credit_expenses=0, other_vehicle_expenses=0
    )
    data["allocations"][0]["expenses"][0]["amount"] = 15000
    data["allocations"][1]["expenses"][0]["amount"] = 5000
    result = calculate(data)
    assert sum(row["federal_taxable_earnings"] for row in result["annual_tax_groups"]) == 0
    assert result["cash"] == 15000
    assert result["annual_tax_groups"][0]["nj_total_income"] == 0


def test_unfunded_distribution_cannot_use_all_reserved_expenses():
    data = payload()
    data.update(contributions=[], returns=[])
    data["accounts"][0].update(balance=1000, contribution_basis=500)
    result = calculate(data)
    assert result["annual_tax_groups"][0]["qualified_expenses_used"] == 1000
    assert result["annual_tax_groups"][0]["reserved_but_unused_expenses"] == 9000
    assert result["annual_tax_groups"][1]["gross_distribution"] == 0
    assert result["unallocated_expenses"]["tuition"] == 0
