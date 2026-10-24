"""Unvested cash needs a supplied right; zero marked value cannot produce a distribution."""

from decimal import Decimal

import pytest

from wealthlab.employment.compensation_example import synthetic
from wealthlab.household.projection import project


@pytest.mark.parametrize(
    ("confirmed", "purpose"), [(False, "tax_distribution"), (True, "ordinary")]
)
def test_unvested_cash_is_not_automatically_available(confirmed, purpose):
    case = synthetic()
    tranche = case.compensation_plan.tranches[0].model_copy(
        update=dict(unvested_tax_cash_right_confirmed=confirmed)
    )
    events = [
        e.model_copy(update=dict(purpose=purpose)) if e.id == "tax_cash" else e
        for e in case.compensation_plan.events
    ]
    plan = case.compensation_plan.model_copy(update=dict(tranches=[tranche], events=events))
    rows = project(case.model_copy(update=dict(compensation_plan=plan)))
    assert rows[4]["employer_distribution_cash"] == 0
    assert rows[4]["employer_distribution_not_paid"] == 20000
    assert rows[-1]["net_wealth"] == 295980


def test_total_employer_loss_preserves_zero_balances_without_creating_tax_deductions():
    case = synthetic()
    events = [
        e.model_copy(update=dict(rate=Decimal(-1))) if e.kind == "net_return" else e
        for e in case.compensation_plan.events
    ]
    plan = case.compensation_plan.model_copy(update=dict(events=events))
    rows = project(case.model_copy(update=dict(compensation_plan=plan)))
    assert rows[2]["employer_vested"] == rows[2]["employer_unvested_contingent"] == 0
    assert sum(r["employer_distribution_cash"] for r in rows) == 0
    assert rows[11]["annual_tax"]["federal"]["agi"] == 110000
    assert rows[-1]["net_wealth"] == 174980
