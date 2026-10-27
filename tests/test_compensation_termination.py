"""Explicit source facts reconcile actual dollar disposition without creating cash or tax relief."""

from decimal import Decimal

import pytest

from wealthlab.employment.compensation_exit_state import from_rows
from wealthlab.employment.compensation_termination_example import terminated
from wealthlab.household.projection import project


def changed(**updates):
    case = terminated()
    events = [
        event.model_copy(update=updates) if event.kind == "termination" else event
        for event in case.compensation_plan.events
    ]
    return case.model_copy(
        update={"compensation_plan": case.compensation_plan.model_copy(update={"events": events})}
    )


def test_supplied_termination_closes_only_after_actual_distribution_and_forfeiture():
    # 100k cash +20k redemption +90k wages -96k spending -19,020 taxes.
    rows = project(terminated())
    result = from_rows(rows)["award"]
    assert rows[-1]["closing_cash"] == 94980
    assert rows[-1]["net_wealth"] == 194980
    assert rows[11]["annual_tax"]["federal"]["agi"] == 110000
    assert result["contractual_exit_proven"] is True
    assert result["conditional_on_supplied_facts"]
    assert result["contract_units"] == result["separate_deferred_value"] == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_date", None),
        ("source_reference", ""),
        ("unit_label", ""),
        ("contract_terminated", None),
        ("remaining_units", None),
        ("remaining_deferred_value", None),
        ("remaining_cash_due", None),
        ("no_future_rights", None),
        ("no_future_contract_obligations", None),
        ("exit_tax_recognition_supplied", None),
    ],
)
def test_missing_termination_facts_withhold_exit_only_and_preserve_cash(field, value):
    rows = project(changed(**{field: value}))
    result = from_rows(rows)["award"]
    assert result["contractual_exit_proven"] is None
    assert result["termination_status"] == "unresolved"
    assert rows[-1]["closing_cash"] == 94980


@pytest.mark.parametrize(
    "field,value",
    [
        ("contract_terminated", False),
        ("remaining_units", Decimal(1)),
        ("remaining_deferred_value", Decimal(5000)),
        ("remaining_cash_due", Decimal(500)),
        ("no_future_rights", False),
        ("no_future_contract_obligations", False),
        ("exit_tax_recognition_supplied", False),
    ],
)
def test_remaining_rights_or_obligations_cannot_be_erased_by_zero_marked_value(field, value):
    rows = project(changed(**{field: value}))
    result = from_rows(rows)["award"]
    assert result["dollar_positions_zero"]
    assert result["contractual_exit_proven"] is False
    assert result["termination_status"] == "not_reconciled"
