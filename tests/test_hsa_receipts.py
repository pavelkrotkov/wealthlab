"""Receipt use is shared, date-aware and excludes previously deducted/reimbursed amounts."""

import pytest
from test_hsa_cash import calculate, payload


def test_a_receipt_cannot_be_reused_by_another_spouse():
    result = calculate(payload())
    first, second = result["orders"][3:5]
    assert first["qualified"] == 1500  # $3,000 less $1,000 reimbursed and $500 deducted.
    assert first["unfilled"] == 500
    assert second["qualified"] == 0
    assert second["federal_taxable"] == 1000
    assert result["receipt_remaining"]["medical"] == 0


def test_receipts_before_hsa_establishment_cannot_become_tax_free():
    row = calculate(payload())["orders"][-1]
    assert row["qualified"] == 0
    assert row["federal_taxable"] == 2000
    assert row["federal_additional_tax"] == 400


def test_future_payment_does_not_supply_a_current_reimbursement_budget():
    data = payload()
    data["medical_receipts"][0]["paid"] = "2027-01-01"
    row = calculate(data)["orders"][3]
    assert row["funded"] == 0
    assert row["unfilled"] == 2000


@pytest.mark.parametrize(("when", "expected"), [("2026-06-30", 200), ("2026-07-01", 0)])
def test_hsa_age65_exception_does_not_remove_ordinary_income(when, expected):
    data = payload()
    data["withdrawals"][1].update(date=when, receipt_ids=[])
    row = next(row for row in calculate(data)["orders"] if row["id"] == "after_65")
    assert row["federal_taxable"] == 1000
    assert row["federal_additional_tax"] == expected
    assert (row["owner"], row["account"]) == ("spouse", "spouse_hsa")


def test_disability_date_removes_only_additional_tax():
    data = payload()
    data["owners"][0]["disabled_since"] = "2026-08-01"
    row = calculate(data)["orders"][-1]
    assert row["federal_taxable"] == 2000
    assert row["federal_additional_tax"] == 0
