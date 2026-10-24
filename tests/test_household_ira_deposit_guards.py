"""Cash funding cannot prove eligibility, and manual deductions cannot be counted twice."""

import pytest

from tests.ira_deposit_household_cases import one_year
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.ira_deposit_household_example import synthetic


@pytest.mark.parametrize(
    "path,value,message",
    [
        (
            ("ira_plan", "contributions", "complete_annual_elections_and_context_confirmed"),
            False,
            "Confirm complete annual IRA",
        ),
        (("ira_plan", "contributions", "years", 0, "filing"), "single", "filing status"),
        (
            ("ira_plan", "contributions", "orders", 0, "id"),
            "household_ira_funding_1",
            "reserved funding prefix",
        ),
        (
            ("tax_plan", "cases", 0, "federal_income", "deductible_ira_contributions"),
            "1",
            "Remove manual IRA",
        ),
    ],
)
def test_invalid_context_blocks(path, value, message):
    data = one_year().model_dump(mode="json")
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data))


def test_missing_context_year_blocks_before_funding():
    data = synthetic().model_dump(mode="json")
    data["ira_plan"]["contributions"]["years"] = data["ira_plan"]["contributions"]["years"][:1]
    with pytest.raises(ValueError, match="every household year"):
        project(Scenario.model_validate(data))


def test_cash_without_earned_compensation_cannot_support_actual_ira_elections():
    data = one_year().model_dump(mode="json")
    data["incomes"] = []
    data["tax_plan"]["income_rules"] = []
    with pytest.raises(ValueError, match="exceeds supported W-2 compensation"):
        project(Scenario.model_validate(data))


def test_saved_original_reproduces_dynamic_funding_without_mutation():
    s = one_year()
    before = s.model_dump_json()
    rows = project(s)
    assert s.model_dump_json() == before
    assert project(Scenario.model_validate_json(before)) == rows
