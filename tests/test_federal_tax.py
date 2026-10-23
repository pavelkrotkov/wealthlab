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
    """2025 joint brackets on $468,500 taxable yield $104,046.

    Employee payroll is 6.2% of $176,100 plus 1.45% of $500,000,
    plus 0.9% of wages above the joint $250,000 Medicare threshold.
    """
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


def test_qualified_dividends_and_niit_are_counted_once():
    """The added dividends remain in the 15% capital-gain bracket.

    MAGI already exceeds the NIIT threshold, so all $20,000 receives the
    3.8% surtax: $3,000 + $760, with no change to wage payroll taxes.
    """
    before = annual(wages_primary=Decimal(300_000))
    after = annual(
        wages_primary=Decimal(300_000),
        dividends=Decimal(20_000),
        qualified_dividends=Decimal(20_000),
    )
    assert after["niit"] == 760
    assert after["total"] - before["total"] == 3760
    assert after["employee_payroll"] == before["employee_payroll"]
