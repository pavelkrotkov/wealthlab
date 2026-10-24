"""Missing context and forecast overrides must fail before Medicare funding."""

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.medicare import run
from wealthlab.retirement.medicare_household_example import synthetic


@pytest.mark.parametrize(
    "flag",
    [
        "direct_billing_without_benefit_withholding_confirmed",
        "costs_excluded_from_other_expenses_confirmed",
        "complete_household_tax_history_confirmed",
    ],
)
def test_confirmations_are_required(flag):
    case = synthetic()
    plan = case.medicare_plan.model_copy(update={flag: False})
    with pytest.raises(ValueError, match="Confirm direct"):
        project(case.model_copy(update=dict(medicare_plan=plan)))


def test_future_static_history_cannot_override_completed_household_returns():
    case = synthetic()
    source = case.medicare_plan.case
    forecast = source.income_history[0].model_copy(update=dict(year=2026))
    source = source.model_copy(update=dict(income_history=[forecast]))
    plan = case.medicare_plan.model_copy(update=dict(case=source))
    with pytest.raises(ValueError, match="only pre-projection"):
        project(case.model_copy(update=dict(medicare_plan=plan)))


def test_household_profile_cannot_run_as_standalone_cash_case():
    with pytest.raises(ValueError, match="household workbench"):
        run(synthetic().medicare_plan.case)


def test_missing_required_prior_return_is_not_assumed_zero():
    case = synthetic()
    source = case.medicare_plan.case.model_copy(update=dict(income_history=[]))
    plan = case.medicare_plan.model_copy(update=dict(case=source))
    with pytest.raises(ValueError, match="Missing two-year"):
        project(case.model_copy(update=dict(medicare_plan=plan)))
