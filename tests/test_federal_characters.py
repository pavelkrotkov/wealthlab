"""Character and explicit future scaling checks beyond ordinary wage brackets."""

from decimal import Decimal as D

from wealthlab.tax.annual import synthetic
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.federal import calculate
from wealthlab.tax.policy import TaxPolicy


def test_collectibles_use_28_percent_ceiling_plus_niit():
    case = synthetic()
    base = FederalIncome(wages_primary=D(500000))
    gains = FederalIncome(
        wages_primary=D(500000), long_term=D(100000), collectibles_component=D(100000)
    )
    before = calculate(case.filing, base, case.federal_deductions, case.policy)
    after = calculate(case.filing, gains, case.federal_deductions, case.policy)
    # Ordinary marginal rates exceed 28%; all extra income is subject to NIIT.
    assert after["income_tax"] - before["income_tax"] == 31800
    assert after["niit"] - before["niit"] == 3800


def test_indexed_hypothesis_scales_income_and_all_dollar_parameters():
    case = synthetic()
    before = calculate(case.filing, case.federal_income, case.federal_deductions, case.policy)
    income = FederalIncome(wages_primary=D(220000))
    policy = TaxPolicy(year=2026, mode="index_2025", annual_index=0.1)
    after = calculate(case.filing, income, case.federal_deductions, policy)
    assert after["total"] == before["total"] * D("1.1")
    assert "Hypothetical" in after["policy"]
