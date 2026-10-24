"""A supported collection context is required before gross claims become net receipts."""

from decimal import Decimal

import pytest

from tests.test_social_household_work import early_case
from wealthlab.household.projection import project
from wealthlab.retirement.social_medicare_example import synthetic
from wealthlab.tax.projection_inputs import IncomeRule


def test_current_premium_context_requires_confirmation():
    case = synthetic()
    plan = case.medicare_plan.model_copy(update=dict(ssa_current_premiums_context_confirmed=False))
    with pytest.raises(ValueError, match="Confirm standard current-premium"):
        project(case.model_copy(update=dict(medicare_plan=plan)))


def test_manual_cash_cannot_replace_generated_claims_in_ssa_collection_mode():
    with pytest.raises(ValueError, match="requires generated household claims"):
        project(synthetic().model_copy(update=dict(social_security=None)))


def test_small_own_record_with_spousal_excess_requires_combined_collection_rules():
    case = synthetic()
    members = list(case.social_security.members)
    members[1] = members[1].model_copy(update=dict(pia_january_2026=Decimal(100)))
    claims = case.social_security.model_copy(update=dict(members=members))
    with pytest.raises(ValueError, match="sufficient active benefit"):
        project(case.model_copy(update=dict(social_security=claims)))


def test_benefit_start_cannot_silently_ignore_unpaid_prior_medical_bills():
    case = synthetic()
    accounts = [
        a.model_copy(update=dict(balance=Decimal(0))) if a.wrapper == "cash" else a
        for a in case.accounts
    ]
    with pytest.raises(ValueError, match="Unpaid Medicare bills at benefit start"):
        project(case.model_copy(update=dict(accounts=accounts)))


def test_ssa_premium_mode_cannot_bypass_the_pre_fra_work_guard():
    case = early_case()
    wage = case.incomes[0].model_copy(update=dict(stop_at_retirement=True))
    rule = IncomeRule(income_id=wage.id, federal="wages_primary", new_jersey="wages")
    taxes = case.tax_plan.model_copy(update=dict(income_rules=[rule]))
    plan = synthetic().medicare_plan
    with pytest.raises(ValueError, match="Pre-FRA benefits with annual wages"):
        project(case.model_copy(update=dict(incomes=[wage], tax_plan=taxes, medicare_plan=plan)))
