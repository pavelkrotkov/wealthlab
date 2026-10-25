"""Whole supplied profiles conserve the original wallet; fees need not be proportional."""

from copy import deepcopy

import pytest
from optimization_drilling_cases import envelope, inputs, offer, opaque_profile

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.optimization.drilling_apply import apply
from wealthlab.optimization.drilling_exits import completed
from wealthlab.optimization.drilling_profiles import validate_offers


@pytest.mark.parametrize(
    ("selected", "cash"), [("well", 140000), ("shares", 200000), ("decline", 200000)]
)
def test_actual_reference_and_explicit_no_entry_spend_only_actual_original_capital(selected, cash):
    household, offers, confirmed, scope = inputs()
    data = household.model_dump(mode="json")
    before = deepcopy(data)
    apply(data, offers, selected, confirmed, scope)
    assert data["accounts"] == before["accounts"]
    case = Scenario.model_validate(data)
    rows = project(case)
    assert rows[-1]["closing_cash"] == cash
    assert completed(case, rows[-1])
    assert confirmed.full_tax_optimization_supported is False


def test_independently_supplied_smaller_profile_retains_flat_fee_and_opaque_exit_quote():
    household, _, _, _ = inputs()
    smaller = offer("complete_smaller", opaque_profile(household))
    confirmed, scope = envelope(household, [smaller])
    validate_offers(household, [smaller], confirmed, scope)
    data = household.model_dump(mode="json")
    apply(data, [smaller], smaller.id, confirmed, scope)
    rows = project(Scenario.model_validate(data))
    assert rows[-1]["closing_cash"] == 185000
    assert rows[-1]["drilling_call_funded"] == 40000
    assert rows[-1]["drilling_paid_costs"]["manager_fee"] == 10000
    assert rows[-1]["drilling_exit_cash"] == 25000
