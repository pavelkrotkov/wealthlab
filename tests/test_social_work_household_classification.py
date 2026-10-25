"""Unsupported benefit offsets and unclassified wage sources block at the input boundary."""

import pytest
from social_work_household_cases import case, payload

from wealthlab.employment.compensation_example import synthetic as employer_example
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.social_medicare_example import synthetic as withholding_example
from wealthlab.retirement.social_work_household_validation import validate


@pytest.mark.parametrize(
    "field, value, match",
    [
        ("tax_plan", None, "annual tax plan"),
        ("compensation_plan", employer_example().compensation_plan, "earned-month classification"),
        ("medicare_plan", withholding_example().medicare_plan, "Medicare SSA withholding"),
    ],
)
def test_unsupported_classification_needs_its_own_adapter(field, value, match):
    scenario = case().model_copy(update={field: value})
    with pytest.raises(ValueError, match=match):
        validate(scenario)


def test_spouse_wage_rule_cannot_disappear_in_a_single_member_household():
    raw = payload()
    raw["tax_plan"]["income_rules"][0]["federal"] = "wages_spouse"
    with pytest.raises(ValueError, match="Wage tax character must match"):
        project(Scenario.model_validate(raw))
