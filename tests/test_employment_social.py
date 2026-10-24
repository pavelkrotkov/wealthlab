"""Actual work decisions reach the Social Security wage guard before any claim is generated."""

import pytest

from tests.test_social_household_work import early_case
from wealthlab.employment.inputs import EmploymentPlan, WagePath
from wealthlab.household.projection import project
from wealthlab.retirement.social_household import prepare
from wealthlab.tax.projection_inputs import IncomeRule


def test_no_work_path_clears_future_wages_before_pre_fra_claim_validation():
    case = early_case()
    rule = IncomeRule(income_id="interest", federal="wages_primary", new_jersey="wages")
    tax = case.tax_plan.model_copy(update=dict(income_rules=[rule]))
    case = case.model_copy(update=dict(tax_plan=tax))
    with pytest.raises(ValueError, match="Pre-FRA benefits with annual wages"):
        prepare(case)
    path = WagePath(
        id="no_work",
        provenance="illustration",
        owner="person",
        income_ids=["interest"],
        opening_multiplier=0,
        changes=[],
    )
    plan = EmploymentPlan(paths=[path])
    rows = project(case.model_copy(update=dict(employment_plan=plan)))
    assert sum(r["income"] for r in rows) == sum(r["social_security_cash"] for r in rows)
    assert sum(r["income"] for r in rows) > 0
