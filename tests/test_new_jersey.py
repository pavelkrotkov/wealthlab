"""Synthetic full-year return examples use independent form arithmetic."""

from decimal import Decimal as D

from wealthlab.tax.filing import Filing
from wealthlab.tax.new_jersey import calculate
from wealthlab.tax.nj_business import BusinessIncome
from wealthlab.tax.nj_facts import NJDeductions, NJIncome
from wealthlab.tax.nj_retirement import RetirementEligibility


def joint(age=40):
    return Filing(status="joint", age_primary=age, age_spouse=age, dependents=[])


def test_wages_and_disposition_losses_stay_separate():
    result = calculate(joint(), NJIncome(wages=D(200000), dispositions=D(-30000)), NJDeductions())
    # $200k gross less two $1k exemptions; Table B: 198000*.0637-4042.50.
    assert result["taxable_income"] == 198000
    assert result["income_tax"] == D("8570.10")
    assert result["business_carry"] == []


def test_business_adjustment_changes_taxable_not_gross_income():
    business = BusinessIncome(partnership=D(40000), rents=D(-60000))
    result = calculate(joint(), NJIncome(wages=D(200000), business=business), NJDeductions())
    assert result["gross_income"] == 240000
    assert result["business_adjustment"] == 20000
    assert result["taxable_income"] == 218000
    assert result["income_tax"] == D("9844.10")


def test_property_deduction_beats_credit_at_high_income():
    result = calculate(
        joint(),
        NJIncome(wages=D(200000)),
        NJDeductions(qualifying_property_tax=D(20000), property_eligible=True),
    )
    assert result["property_deduction"] == 15000
    assert result["property_credit"] == 0
    assert result["income_tax"] == D("7614.60")


def test_retirement_exclusion_precedes_filing_threshold():
    eligible = RetirementEligibility(qualified_pension=D(50000))
    result = calculate(
        joint(67),
        NJIncome(pension=D(50000), retirement=eligible),
        NJDeductions(qualifying_property_tax=D(5000), property_eligible=True),
    )
    assert result["gross_income"] == 0
    assert result["below_filing_threshold"]
    assert result["income_tax"] == -50
    assert result["property_credit"] == 50


def test_property_credit_for_under65_requires_gross_above_threshold():
    inputs = NJDeductions(qualifying_property_tax=D(100), property_eligible=True)
    low = calculate(joint(), NJIncome(wages=D(20000)), inputs)
    above = calculate(joint(), NJIncome(wages=D(20001)), inputs)
    assert low["income_tax"] == 0
    assert above["property_credit"] == 50
