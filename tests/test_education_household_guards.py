"""Unconfirmed bills, duplicate deductions and unknown education accounts block."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.education_household_example import synthetic


@pytest.mark.parametrize(
    "field",
    [
        "complete_context_confirmed",
        "qualified_net_expenses_separate_from_other_budgets_confirmed",
        "contributions_belong_to_filing_unit_confirmed",
    ],
)
def test_each_education_confirmation_is_required(field):
    data = synthetic().model_dump(mode="json")
    data["education_plan"][field] = False
    with pytest.raises(ValueError, match="Confirm complete 529"):
        project(Scenario.model_validate(data))


def test_unknown_tuition_source_has_a_user_facing_error():
    data = synthetic().model_dump(mode="json")
    data["education_plan"]["tuition"][0]["source"] = "missing"
    with pytest.raises(ValueError, match="Unknown household 529 account"):
        project(Scenario.model_validate(data))


def test_manual_njbest_deduction_cannot_duplicate_actual_funding():
    data = synthetic().model_dump(mode="json")
    data["tax_plan"]["cases"][0]["nj_deductions"]["njbest"] = "1"
    with pytest.raises(ValueError, match="Remove manual NJBEST"):
        project(Scenario.model_validate(data))


def test_published_future_year_cannot_silently_reuse_current_law():
    data = synthetic().model_dump(mode="json")
    data["education_plan"]["rule_mode"] = "published"
    with pytest.raises(ValueError, match="Published contribution rules"):
        project(Scenario.model_validate(data))
