"""Incomplete tax assumptions or unreconciled employer assets cannot produce a projection."""

from datetime import date
from decimal import Decimal

import pytest

from wealthlab.employment.compensation_example import synthetic
from wealthlab.employment.compensation_projection import prepare
from wealthlab.household.projection import project


@pytest.mark.parametrize(
    "flag",
    ["tax_inputs_exclude_plan_events_confirmed", "all_plan_tax_recognition_supplied_confirmed"],
)
def test_unconfirmed_tax_context_is_blocked(flag):
    case = synthetic()
    plan = case.compensation_plan.model_copy(update={flag: False})
    with pytest.raises(ValueError, match="Confirm complete supplied plan taxes"):
        prepare(case.model_copy(update=dict(compensation_plan=plan)))


def test_vested_opening_values_must_match_the_employer_account():
    case = synthetic()
    tranche = case.compensation_plan.tranches[0].model_copy(update=dict(opening_vested=Decimal(1)))
    plan = case.compensation_plan.model_copy(update=dict(tranches=[tranche]))
    with pytest.raises(ValueError, match="balances must equal"):
        prepare(case.model_copy(update=dict(compensation_plan=plan)))


def test_unknown_tranches_and_out_of_horizon_dates_are_rejected():
    case = synthetic()
    event = case.compensation_plan.events[0]
    for update in (dict(tranche="missing"), dict(date=date(2029, 1, 1))):
        changed = event.model_copy(update=update)
        plan = case.compensation_plan.model_copy(update=dict(events=[changed]))
        with pytest.raises(ValueError):
            prepare(case.model_copy(update=dict(compensation_plan=plan)))


def test_contingent_or_locked_value_does_not_fund_spending_automatically():
    case = synthetic()
    accounts = [
        a.model_copy(update=dict(balance=Decimal(0))) if a.wrapper == "cash" else a
        for a in case.accounts
    ]
    tax = case.tax_plan.model_copy(update=dict(income_rules=[]))
    case = case.model_copy(
        update=dict(accounts=accounts, incomes=[], tax_plan=tax, employment_plan=None)
    )
    first = project(case)[0]
    assert first["closing_cash"] == 0
    assert first["employer_unvested_contingent"] == 90000
    assert first["funding_shortfall"] == 4000
