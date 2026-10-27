"""Whole new-life purchase choices fund actual premiums without creating starting wealth."""

import pytest
from optimization_new_life_cases import case

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_original_capital_and_actual_selected_exit_reconcile_with_held_out_cash(result):
    candidates = result["candidates"]
    assert [c["median_real_after_tax_exit_wealth"] for c in candidates] == [251999, 252099]
    assert all(
        c["opening_allocation_audit"]["allocated_opening_wealth"] == 300000 for c in candidates
    )
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 252099
    assert result["configured_validation_passed"]


def test_premiums_and_gain_use_the_existing_wallet_and_tax_return_once(result):
    rows = result["selected_training"]["details"][0]["rows"]
    assert sum(r["life_premiums_paid"] for r in rows) == 2000
    assert sum(r["life_cash_received"] for r in rows) == 2100
    assert rows[11]["annual_tax"]["federal"]["agi"] == 100
    assert rows[-1]["account_balances"]["new_policy"] == 0


def test_empty_selection_does_not_create_a_policy_and_preserves_the_independent_need():
    profile = case()
    household, _ = compile_candidate(profile, [profile.dimensions[-1].choices[0]])
    assert household.accounts == profile.household.accounts
    assert household.life_plan.holdings == []
    assert household.life_plan.insurance_need_by_owner == dict(person_a=0)
