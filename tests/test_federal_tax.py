"""Independent federal bracket/payroll cases catch tax character and double counting."""

from decimal import Decimal

import pytest

from wealthlab.tax.facts import Deductions, FederalIncome
from wealthlab.tax.federal import calculate
from wealthlab.tax.filing import Filing
from wealthlab.tax.policy import TaxPolicy


def annual(**income):
    filing = Filing(status="joint", age_primary=40, age_spouse=40, dependents=[])
    policy = TaxPolicy(year=2025, mode="package_law", annual_index=0)
    return calculate(filing, FederalIncome(**income), Deductions(), policy)


def test_high_wages_count_additional_medicare_once():
    result = annual(wages_primary=Decimal(500_000))
    assert result["income_tax"] == Decimal(104_046)
    assert result["employee_payroll"] == Decimal("20418.20")
    assert result["additional_medicare"] == 2250
    assert result["total"] == Decimal("124464.20")


def test_low_income_preserves_unused_capital_deduction():
    result = annual(short_term=Decimal(-10000))
    assert result["short_carry"] == 10000
    assert result["long_carry"] == 0
    assert result["taxable_income"] == 0


def test_mixed_character_and_carry():
    result = annual(
        wages_primary=Decimal(150_000), short_term=Decimal(-10_000), long_term=Decimal(4_000)
    )
    assert result["short_carry"] == 3000
    assert result["agi"] == 147000
    assert result["income_tax"] == Decimal(15238)


def test_invalid_policy_and_input_scope():
    with pytest.raises(ValueError, match="2036"):
        TaxPolicy(year=2050, mode="package_law", annual_index=0).valuation()
    with pytest.raises(ValueError, match="included"):
        FederalIncome(dividends=Decimal(1), qualified_dividends=Decimal(2))
