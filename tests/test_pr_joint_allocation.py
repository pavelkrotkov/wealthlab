"""Independent joint-filing oracle refutes confusing the year axis with single status."""

from decimal import Decimal

from wealthlab.tax.federal import calculate as baseline_federal
from wealthlab.tax.pr_examples import synthetic
from wealthlab.tax.pr_federal import calculate
from wealthlab.tax.pr_inputs import income


def test_joint_933_allocation_scales_joint_standard_and_keeps_shared_policy_intact():
    case = synthetic()
    pr = case.income[0].model_copy(
        update={"federal_amount": Decimal(200000), "pr_amount": Decimal(200000)}
    )
    us = pr.model_copy(
        update={
            "kind": "interest",
            "federal_amount": Decimal(80000),
            "pr_amount": Decimal(80000),
            "federal_source": "US",
            "pr_source": "US",
        }
    )
    filing = case.baseline.filing.model_copy(update={"status": "joint", "age_spouse": 40})
    baseline = case.baseline.model_copy(
        update={"filing": filing, "federal_income": income([pr, us])}
    )
    case = case.model_copy(update={"baseline": baseline, "income": [pr, us]})
    result = calculate(case, [us], [])
    # 31,500 x80,000/280,000 =9,000, not the single deduction or full joint.
    # Joint tax:23,850 x10% +(71,000-23,850)x12% =8,043.
    assert result["standard_deduction"] == 9000
    assert result["taxable_income"] == 71000
    assert result["income_tax"] == 8043
    original = baseline_federal(
        filing, baseline.federal_income, baseline.federal_deductions, baseline.policy
    )
    assert original["standard_deduction"] == 31500
