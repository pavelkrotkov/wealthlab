"""Reference closure consumes actual shares/cash/wash, not unused property-book flags."""

from copy import deepcopy

import pytest
from optimization_drilling_cases import inputs

from wealthlab.household.projection import project
from wealthlab.optimization.drilling_exits import completed


@pytest.fixture(scope="module")
def reference():
    household, _, _, _ = inputs()
    plan = household.drilling_plan.model_copy(update={"mode": "liquid_reference"})
    case = household.model_copy(update={"drilling_plan": plan})
    return case, project(case)[-1]


def test_real_reference_book_closes_even_though_property_sale_flags_are_false(reference):
    case, row = reference
    state = row["drilling_audit"]["terminal_state"]
    assert (state["closed"], state["property_sold"]) == (False, False)
    assert completed(case, row)


@pytest.mark.parametrize(
    "location,key,value",
    [
        ("state", "reference_exit_pending", True),
        ("reference_cash", "drilling", "1"),
        ("reference_pending_losses", "federal", "1"),
        ("reference_pending_losses", "nj", "1"),
        ("state", "reference_pending_losses", {}),
        ("state", "reference_cash", {}),
    ],
)
def test_any_actual_reference_cash_or_wash_or_pending_sale_prevents_closure(
    reference, location, key, value
):
    case, row = reference
    damaged = deepcopy(row)
    state = damaged["drilling_audit"]["terminal_state"]
    destination = state if location == "state" else state[location]
    destination[key] = value
    assert completed(case, damaged) is False


def test_remaining_actual_reference_lots_cannot_be_hidden_by_a_zero_account_balance(reference):
    case, row = reference
    damaged = deepcopy(row)
    damaged["drilling_audit"]["reference_lots"] = [{"quantity": "1"}]
    assert completed(case, damaged) is False


def test_unknown_programmatic_mode_cannot_be_treated_as_a_closed_reference_book(reference):
    case, row = reference
    damaged = deepcopy(row)
    plan = case.drilling_plan.model_copy(update={"mode": "unknown"})
    damaged["drilling_audit"]["terminal_state"]["mode"] = "unknown"
    unsupported = case.model_copy(update={"drilling_plan": plan})
    assert completed(unsupported, damaged) is False
