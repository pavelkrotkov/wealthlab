"""Opening option purchases cannot manufacture household capital or historical tax lots.

The independent flat terminal identity is300000-48000-1+496*units. Cash reserve
and complete-exit checks use actual timing, while all native taxes still settle.
"""

import pytest
from optimization_option_cases import case

from wealthlab.household.funding import opening_wealth
from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_original_wealth_and_actual_exit_cash_reconcile_for_zero_one_and_two_units(result):
    outcomes = result["candidates"]
    assert [c["median_real_after_tax_exit_wealth"] for c in outcomes] == [251999, 252495, 252991]
    assert all(c["eligible"] for c in outcomes)
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 252991
    assert result["configured_validation_passed"]


@pytest.mark.parametrize("count", range(3))
def test_each_allocation_moves_source_cash_to_a_new_account_without_changing_wealth(result, count):
    audit = result["candidates"][count]["opening_allocation_audit"]
    assert audit["original_opening_wealth"] == audit["allocated_opening_wealth"] == 300000
    assert audit["cash_debits"] == dict(cash=12000 * count)
    assert audit["new_account_capital"] == (dict(options=12000 * count) if count else {})
    assert audit["new_sleeve_capital"] == {}


def test_zero_units_create_no_account_plan_or_market_binding_and_preserve_original_lots():
    profile = case()
    household, binding = compile_candidate(profile, [profile.dimensions[-1].choices[0]])
    assert household.option_plan is None and binding.options is None
    assert household.accounts == profile.household.accounts
    assert household.lot_plan == profile.household.lot_plan
    assert opening_wealth(household) == 300000


def test_new_units_execute_gross_stock_acquisition_and_disposal_in_the_selected_wallet(result):
    rows = result["selected_training"]["details"][0]["rows"]
    state = rows[-1]["option_mark_audit"][-1]["exit_state"]
    assert [(t["action"], t["quantity"]) for t in state["stock_trades"]] == [
        ("buy", "200"),
        ("sell", "200"),
    ]
    assert state["modeled_cash_exit_complete"]
    assert rows[-1]["account_balances"]["options"] == 0
    assert rows[-1]["closing_cash"] == 252991
