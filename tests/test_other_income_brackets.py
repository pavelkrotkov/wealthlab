"""Positive classified other income shares ordinary brackets without becoming payroll wages."""

from decimal import Decimal

import pytest
from ordinary_income_cases import compute

from wealthlab.tax.policy import TaxPolicy


@pytest.mark.parametrize("year", [2025, 2026, 2036])
def test_other_income_matches_ordinary_brackets_but_retains_only_actual_payroll(year):
    policy = TaxPolicy(year=year, mode="package_law", annual_index=0)
    other = compute(dict(wages_primary=50000, ordinary_noninvestment_income=10000), policy)
    wages = compute(dict(wages_primary=60000), policy)
    assert (other["agi"], other["income_tax"]) == (60000, wages["income_tax"])
    assert other["employee_payroll"] < wages["employee_payroll"]
    assert other["niit"] == 0
    assert "numerical carrier" in other["ordinary_noninvestment_adapter"]


def test_explicit_indexing_scales_the_carrier_like_other_dollar_inputs():
    baseline = compute(dict(ordinary_noninvestment_income=100000))
    future = compute(
        dict(ordinary_noninvestment_income=110000),
        TaxPolicy(year=2026, mode="index_2025", annual_index=0.1),
    )
    assert future["income_tax"] == baseline["income_tax"] * Decimal("1.1")
    assert future["agi"] == 110000
