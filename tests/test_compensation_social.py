"""Noncash employer wages must participate in the same pre-FRA earnings guard as salary."""

from decimal import Decimal

import pytest

from tests.test_social_household_work import early_case
from wealthlab.employment.compensation_events import Allocation
from wealthlab.employment.compensation_example import synthetic
from wealthlab.household.projection import project
from wealthlab.household.records import Account
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome


def test_compensation_wages_are_checked_before_early_benefit_cash_is_generated():
    case = early_case()
    source = synthetic().compensation_plan
    account = Account(
        id="employer_fund",
        provenance="illustration",
        owner="person",
        wrapper="employer",
        currency="USD",
        balance=1,
        monthly_fee=0,
    )
    tranche = source.tranches[0].model_copy(
        update=dict(opening_vested=Decimal(1), opening_unvested=Decimal(0), liquid_from=case.start)
    )
    allocation = Allocation(
        id="wages_without_cash",
        provenance="illustration",
        date=case.start,
        tranche=tranche.id,
        sequence=0,
        kind="allocation",
        federal=FederalIncome(wages_primary=100),
        new_jersey=NJIncome(wages=100),
    )
    plan = source.model_copy(update=dict(tranches=[tranche], events=[allocation]))
    case = case.model_copy(update=dict(accounts=[*case.accounts, account], compensation_plan=plan))
    with pytest.raises(ValueError, match="Pre-FRA benefits with annual wages"):
        project(case)


def test_wage_allocations_cannot_use_the_other_spouses_payroll_record():
    case = synthetic()
    events = [
        e.model_copy(update=dict(federal=FederalIncome(wages_spouse=100)))
        if e.kind == "allocation"
        else e
        for e in case.compensation_plan.events
    ]
    plan = case.compensation_plan.model_copy(update=dict(events=events))
    with pytest.raises(ValueError, match="must match the tranche owner"):
        project(case.model_copy(update=dict(compensation_plan=plan)))
