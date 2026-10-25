"""Eligible ordinary zero-basis plan cash cannot silently grant broader tax treatment."""

from datetime import date

import pytest
from pydantic import ValidationError

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_withdrawal_example import profile, synthetic
from wealthlab.retirement.workplace_withdrawal_inputs import CashProfile, WorkplaceCashOrder
from wealthlab.retirement.workplace_withdrawal_validation import validate, validate_profile


@pytest.mark.parametrize(
    "field",
    [
        "eligible_nonperiodic_cash_distributions_confirmed",
        "fully_vested_zero_federal_and_nj_basis_confirmed",
        "no_inherited_loans_nua_hardship_or_other_special_features_confirmed",
        "complete_distributions_excluded_from_other_inputs_confirmed",
    ],
)
def test_all_legal_and_basis_context_requires_explicit_confirmation(field):
    data = profile()
    data[field] = False
    with pytest.raises(ValueError, match="Confirm"):
        validate_profile(CashProfile.model_validate(data), date(1971, 7, 1), 2027)


@pytest.mark.parametrize(
    "change,message",
    [
        (dict(source="unknown"), "source profiles"),
        (dict(date="2026-02-15"), "first-day"),
        (dict(date="2028-02-01"), "in-horizon"),
        (dict(provenance="unresolved"), "resolved"),
        (dict(date="2025-12-01"), "in-horizon"),
    ],
)
def test_withdrawal_references_and_dates_are_resolved(change, message):
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["orders"][0].update(change)
    with pytest.raises(ValueError, match=message):
        validate(Scenario.model_validate(data))


@pytest.mark.parametrize("federal,nj", [(".19", "0"), (".9", ".2"), (".2", "-.1")])
def test_cash_profile_enforces_mandatory_federal_and_total_withholding(federal, nj):
    order = synthetic().workplace_plan.cash_withdrawals.orders[0].model_dump(mode="json")
    order.update(federal_withholding_rate=federal, nj_withholding_rate=nj)
    with pytest.raises(ValidationError):
        WorkplaceCashOrder.model_validate(order)


def test_rmd_years_are_blocked_instead_of_using_eligible_cash_withholding():
    with pytest.raises(ValueError, match="RMD"):
        validate_profile(CashProfile.model_validate(profile()), date(1960, 1, 1), 2035)


def test_withdrawal_cannot_precede_the_source_plan_separation_date():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["profiles"]["work_pretax"]["separation_date"] = (
        "2026-03-01"
    )
    with pytest.raises(ValueError, match="precede"):
        validate(Scenario.model_validate(data))


def test_roth_plan_cannot_use_the_ordinary_pretax_cash_profile():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["products"]["work_pretax"] = "roth_401k"
    with pytest.raises(ValueError, match="pretax"):
        validate(Scenario.model_validate(data))


def test_separated_source_cannot_accept_new_employee_deferrals():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["orders"] = [
        dict(
            id="new_deferral",
            provenance="illustration",
            date="2026-02-01",
            owner="person_a",
            destination="work_pretax",
            kind="pretax_401k",
            amount=1000,
        )
    ]
    with pytest.raises(ValueError, match="separated source"):
        validate(Scenario.model_validate(data))


def test_1959_owner_before_both_rmd_start_choices_does_not_need_a_choice():
    validate_profile(CashProfile.model_validate(profile()), date(1959, 7, 1), 2027)
    with pytest.raises(ValueError, match="1959"):
        validate_profile(CashProfile.model_validate(profile()), date(1959, 7, 1), 2032)
