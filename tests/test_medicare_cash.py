"""Later cash cures premium arrears but cannot erase the original funding failure."""

from decimal import Decimal

from wealthlab.retirement.medicare import run
from wealthlab.retirement.medicare_example import synthetic
from wealthlab.retirement.medicare_inputs import MedicareCase


def payload():
    return synthetic().model_dump(mode="json")


def calculate(data):
    return run(MedicareCase.model_validate(data))


def test_synthetic_costs_and_cash_reconcile_with_cured_arrears():
    result = run(synthetic())
    assert result["total_due"] == result["total_paid"] == 22929
    assert result["cash"] == 2071
    assert result["outstanding"] == 0
    assert result["cash"] + result["total_paid"] == 25000
    assert len(result["monthly"]) == 42
    assert sum(row["unfunded_at_due"] for row in result["monthly"]) == Decimal("7299.40")


def test_unfunded_bills_are_visible_without_negative_cash():
    data = payload()
    data["receipts"] = []
    result = calculate(data)
    assert result["cash"] == 0
    assert result["total_paid"] == 5000
    assert result["outstanding"] == 17929
    assert result["total_due"] == result["total_paid"] + result["outstanding"]
