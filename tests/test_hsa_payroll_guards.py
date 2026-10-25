"""No wage exclusion without confirmed plan eligibility, complete wages and valid dated orders."""

import pytest

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_validation import validate
from wealthlab.retirement.hsa_payroll_example import synthetic


@pytest.mark.parametrize(
    "flag",
    [
        "qualifying_section125_w2_employee_confirmed",
        "gross_wages_before_salary_reduction_confirmed",
        "complete_elections_and_no_other_payroll_reductions_confirmed",
    ],
)
def test_unconfirmed_eligibility_cannot_create_wage_exclusion(flag):
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"]["payroll"][flag] = False
    with pytest.raises(ValueError, match="Confirm qualifying section125"):
        validate(Scenario.model_validate(data))


@pytest.mark.parametrize(
    "change, message",
    [
        (dict(date="2026-01-15"), "first-day dates"),
        (dict(owner="person_b"), "match the individual account owner"),
        (dict(id="personal_deposit"), "order IDs must be unique"),
        (dict(provenance="unresolved"), "Resolve payroll HSA"),
    ],
)
def test_invalid_salary_election_cannot_enter_the_funding_book(change, message):
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"]["payroll"]["orders"][0].update(change)
    with pytest.raises(ValueError, match=message):
        validate(Scenario.model_validate(data))


def test_wages_already_reduced_or_entered_manually_cannot_be_excluded_again():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"] = None
    data["tax_plan"]["cases"][0]["federal_income"]["wages_primary"] = "500"
    with pytest.raises(ValueError, match="not manual annual wage"):
        validate(Scenario.model_validate(data))
