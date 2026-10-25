"""Real retained-source and fund-basket exits share one household wallet.

All profiles start310000, spend48000 and pay1ordinary-stock commission, yielding
261999. Contributed10000capital is not another deposit when its basket is sold.
"""

import pytest
from optimization_exchange_cases import case

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_retain_half_and_full_profiles_reconcile_the_same_cash_and_heldout_exit(result):
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [261999] * 4
    assert all(c["eligible"] for c in result["candidates"])
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 261999
    assert result["configured_validation_passed"]


@pytest.mark.parametrize("index,quantity", [(0, 0), (1, 50), (2, 100), (3, 100)])
def test_selected_quantities_preserve_the_entire_original_lot_and_account_capital(index, quantity):
    profile = case()
    before = profile.model_dump_json()
    household, _ = compile_candidate(profile, [profile.dimensions[-1].choices[index]])
    original = profile.household.exchange_fund_plan
    assert household.exchange_fund_plan.contribution_quantity == quantity
    assert household.exchange_fund_plan.source_lot == original.source_lot
    assert household.accounts == profile.household.accounts
    assert before == profile.model_dump_json()


def test_retained_source_only_uses_the_actual_source_sale_and_never_opens_a_fund(result):
    audit = result["selected_training"]["details"][0]["rows"][-1]["exchange_fund_audit"]
    assert audit["exit_status"]["modeled_exit_complete"]
    assert not audit["exit_status"]["fund_entered"]
    assert audit["opening_contribution_events"] == []
    assert sum(m["source_sale_cash"] for m in audit["months"]) == 10000
    assert audit["remaining_lots"] == []
