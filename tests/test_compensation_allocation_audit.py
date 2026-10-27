"""Preserved recognition remains immutable, exactly once and independent of closure cash."""

from datetime import date
from decimal import Decimal

import pytest

from wealthlab.employment.compensation import Ledger
from wealthlab.employment.compensation_projection import prepare
from wealthlab.employment.compensation_termination_example import terminated
from wealthlab.employment.compensation_termination_state import pending_allocations
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.household.storage import loads


def test_compiled_source_audit_roundtrips_and_prepares_exactly_once():
    original = terminated()
    before = original.model_dump_json()
    prepared = prepare(original)
    assert original.model_dump_json() == before
    assert prepare(prepared) == prepared
    assert loads(prepared.model_dump_json()) == prepared
    assert [event.id for event in prepared.compensation_plan.compiled_allocations] == ["exit_tax"]
    assert len(prepared.tax_plan.events) == 1
    assert prepared.tax_plan.events[0].cash_received == 0


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "cash"])
def test_compiled_audit_requires_one_exact_zero_cash_tax_record(mutation):
    prepared = prepare(terminated())
    events = list(prepared.tax_plan.events)
    if mutation == "missing":
        events = []
    elif mutation == "duplicate":
        events *= 2
    else:
        events[0] = events[0].model_copy(update={"cash_received": Decimal(1)})
    tax = prepared.tax_plan.model_copy(update={"events": events})
    with pytest.raises(ValueError, match="exactly one zero-cash"):
        prepare(prepared.model_copy(update={"tax_plan": tax}))


def future_tax_case():
    data = terminated().model_dump(mode="json")
    data["compensation_plan"]["events"].append(
        dict(
            id="later_tax",
            tranche="award",
            provenance="illustration",
            sequence=0,
            kind="allocation",
            date="2027-01-01",
            federal=dict(allowed_passive_income="100000"),
            new_jersey=dict(business=dict(partnership="100000")),
        )
    )
    return Scenario.model_validate(data)


def test_late_non_cash_tax_recognition_is_not_dropped_after_contractual_exit():
    case = future_tax_case()
    prepared = prepare(case)
    ledger = Ledger(prepared)
    pending = pending_allocations(ledger, "award", date(2027, 1, 1))
    assert [event["id"] for event in pending] == ["later_tax"]
    assert [
        event["id"] for event in pending_allocations(Ledger(case), "award", date(2027, 1, 1))
    ] == ["later_tax"]
    rows = project(case)
    # Joint frozen federal tax $7,743. NJ uses the $98,000-98,050 table
    # band midpoint: $98,025 * .05525 - $2,775 = $2,640.88125 → $2,641.
    # Final $94,980 cash less $10,384 later tax; allocation deposits nothing.
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 100000
    assert rows[-1]["closing_cash"] == Decimal("84596.00")
