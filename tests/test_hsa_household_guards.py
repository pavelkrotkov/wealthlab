"""Unconfirmed histories, unpaid bills and unsupported tax treatment cannot fund cash."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_example import synthetic
from wealthlab.retirement.medicare_household_template import template as medicare_template


@pytest.mark.parametrize(
    "field",
    [
        "conditional_nj_treatment_confirmed",
        "cash_only_accounts_and_complete_context_confirmed",
        "receipts_paid_before_projection_confirmed",
        "employer_funding_excluded_from_other_nj_wages_confirmed",
    ],
)
def test_each_hsa_confirmation_is_required(field):
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"][field] = False
    with pytest.raises(ValueError, match="Confirm complete cash HSAs"):
        project(Scenario.model_validate(data))


@pytest.mark.parametrize(
    "path,value,message",
    [
        (("hsa_plan", "medical_receipts", 0, "paid"), "2026-01-01", "paid before the projection"),
        (
            ("hsa_plan", "withdrawals", 0, "mode"),
            "allow_nonqualified",
            "Nonqualified household HSA",
        ),
        (
            ("tax_plan", "cases", 0, "federal_income", "deductible_hsa_contributions"),
            "1",
            "Remove manual HSA deductions",
        ),
    ],
)
def test_invalid_hsa_inputs_block(path, value, message):
    data = synthetic().model_dump(mode="json")
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data))


def test_confirmed_medicare_enrollment_cannot_keep_conflicting_hsa_eligibility():
    case = synthetic()
    plan = medicare_template(case)
    plan.update(
        direct_billing_without_benefit_withholding_confirmed=True,
        costs_excluded_from_other_expenses_confirmed=True,
        complete_household_tax_history_confirmed=True,
    )
    plan["case"]["complete_context"] = True
    for record in plan["case"]["coverage"]:
        record["eligibility_confirmed"] = True
    data = case.model_dump(mode="json")
    data["medicare_plan"] = plan
    with pytest.raises(ValueError, match="agree with confirmed household enrollment"):
        project(Scenario.model_validate(data))


def test_later_year_cannot_invent_an_earlier_hsa_establishment_date():
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"]["years"][1]["owners"][0]["established"] = "2019-01-01"
    with pytest.raises(ValueError, match="establishment history must remain consistent"):
        project(Scenario.model_validate(data))


def test_excess_employer_funding_cannot_silently_disappear_at_the_limit():
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"]["contributions"][1]["amount"] = "10000"
    with pytest.raises(ValueError, match="Excess employer HSA funding"):
        project(Scenario.model_validate(data))


def test_account_holder_needs_a_known_establishment_date():
    data = synthetic().model_dump(mode="json")
    for context in data["hsa_plan"]["years"]:
        context["owners"][0]["established"] = None
    with pytest.raises(ValueError, match="known establishment date"):
        project(Scenario.model_validate(data))
