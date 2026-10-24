"""Direct billing cannot silently borrow standalone cash or become benefit withholding."""

from datetime import date
from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.medicare_household_example import synthetic
from wealthlab.retirement.medicare_inputs import MedicareDetermination
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


@pytest.mark.parametrize(
    "change,match",
    [
        (dict(opening_cash=Decimal(1000)), "household cash"),
        (dict(income_policy="supplied_full_horizon"), "completed household returns"),
    ],
)
def test_standalone_cash_and_income_profile_are_rejected(change, match):
    case = synthetic()
    source = case.medicare_plan.case.model_copy(update=change)
    plan = case.medicare_plan.model_copy(update=dict(case=source))
    with pytest.raises(ValueError, match=match):
        project(case.model_copy(update=dict(medicare_plan=plan)))


def test_manual_benefits_require_the_withholding_adapter():
    case = synthetic()
    event = TaxEvent(
        date=date(2026, 1, 1),
        description="Supplied gross benefit",
        cash_received=1000,
        federal=FederalIncome(social_security=1000),
        new_jersey=NJIncome(),
    )
    plan = case.tax_plan.model_copy(update=dict(events=[event]))
    with pytest.raises(ValueError, match="Benefit withholding"):
        project(case.model_copy(update=dict(tax_plan=plan)))


def test_conditional_redetermination_is_not_automatically_granted_in_household():
    case = synthetic()
    determination = MedicareDetermination(
        id="conditional",
        provenance="assumption",
        member="person_a",
        premium_year=2026,
        income="joint_2025",
        method="conditional_ssa_redetermination",
    )
    source = case.medicare_plan.case.model_copy(update=dict(determinations=[determination]))
    plan = case.medicare_plan.model_copy(update=dict(case=source))
    with pytest.raises(ValueError, match="standalone Medicare workbench"):
        project(case.model_copy(update=dict(medicare_plan=plan)))
