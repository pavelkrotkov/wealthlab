"""Actual source bookkeeping, not zero equity, proves the native exit in each mode."""

from copy import deepcopy

import pytest
from optimization_drilling_cases import inputs

from wealthlab.household.projection import project
from wealthlab.optimization.drilling_exits import completed


@pytest.fixture(scope="module")
def actual():
    household, _, _, _ = inputs()
    return household, project(household)[-1]


@pytest.mark.parametrize(
    "location,key,value",
    [
        ("state", "closed", False),
        ("state", "property_sold", False),
        ("state", "cash", "1"),
        ("state", "property_value", "1"),
        ("state", "call_owed", "1"),
        ("creditors", "liability_cost", "1"),
        ("basis", "federal", "1"),
        ("basis", "nj", "1"),
        ("basis", "at_risk", "1"),
        ("tangible_basis", "federal", "1"),
        ("state", "cash", "NaN"),
        ("state", "cash", False),
        ("state", "cash", None),
        ("state", "creditors", {}),
        ("state", "creditors", None),
    ],
)
def test_any_remaining_actual_asset_debt_call_basis_or_malformed_state_prevents_closure(
    actual, location, key, value
):
    household, row = actual
    damaged = deepcopy(row)
    state = damaged["drilling_audit"]["terminal_state"]
    destination = state if location == "state" else state[location]
    destination[key] = value
    assert completed(household, damaged) is False


def test_missing_raw_evidence_and_future_tax_facts_never_mean_a_completed_exit(actual):
    household, row = actual
    assert completed(household, row)
    assert completed(household, {}) is False
    assert completed(household, None) is False
    missing = deepcopy(row)
    missing["drilling_audit"].pop("terminal_state")
    assert completed(household, missing) is False
    future = deepcopy(row)
    future["drilling_audit"]["future_tax_events"] = [{"unrecognized": True}]
    assert completed(household, future) is False


def test_missing_owned_account_balance_cannot_certify_a_matched_book_exit(actual):
    household, row = actual
    missing = deepcopy(row)
    missing.pop("account_balances")
    assert completed(household, missing) is False
    residual = deepcopy(row)
    residual["account_balances"]["drilling"] = 1
    assert completed(household, residual) is False
