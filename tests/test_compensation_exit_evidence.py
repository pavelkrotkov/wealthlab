"""Value writeoff, cash redemption and contractual termination remain different evidence."""

from decimal import Decimal

import pytest

from wealthlab.employment.compensation_example import synthetic
from wealthlab.employment.compensation_exit_state import from_rows
from wealthlab.household.projection import project


@pytest.fixture(scope="module")
def baseline_rows():
    return project(synthetic())


@pytest.fixture(scope="module")
def loss_rows():
    case = synthetic()
    events = [
        event.model_copy(update={"rate": Decimal(-1)}) if event.kind == "net_return" else event
        for event in case.compensation_plan.events
    ]
    plan = case.compensation_plan.model_copy(update={"events": events})
    return project(case.model_copy(update={"compensation_plan": plan}))


def test_total_market_loss_does_not_become_cash_redemption_or_contractual_closure(loss_rows):
    # Opening20,000 vested +90,000 unvested after grant are written to zero.
    # The separate20,000 tax allocation survives; no fictitious loss deduction.
    result = from_rows(loss_rows)["award"]
    assert result["dollar_positions_zero"]
    assert result["cash_distributed"] == 0
    assert result["market_value_losses"] == 110000
    assert result["zeroed_by_market_event_ids"] == ["growth"]
    assert result["contractual_exit_proven"] is None
    assert loss_rows[11]["annual_tax"]["federal"]["agi"] == 110000
    assert loss_rows[-1]["net_wealth"] == 174980


def test_actual_distributions_and_unknown_rights_remain_in_native_evidence(baseline_rows):
    # Supplied unvested tax cash20,000 +later vested distribution10,000.
    # The remaining91,000 is still an employer claim, not spendable wallet cash.
    result = from_rows(baseline_rows)["award"]
    assert result["cash_distributed"] == 30000
    assert result["account_balance"] == result["account_vested_value"] == 91000
    assert result["account_reconciles"]
    assert result["separate_deferred_value"] is None
    assert result["future_rights_after_horizon"] is None
    assert result["pending_tax_obligations"] is None
