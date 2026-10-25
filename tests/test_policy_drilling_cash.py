"""Native property/ref/no-entry compare the same capital and recognize actual exit taxes."""

import pytest
from optimization_drilling_search_cases import case

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.product_exits import complete
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_actual_cost_and_exit_identity_matches_frozen_held_out_selection(result):
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        140000,
        200000,
        200000,
    ]
    assert result["configured_validation_passed"]
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 200000
    assert all(
        c["opening_allocation_audit"]["allocated_opening_wealth"] == 200000
        for c in result["candidates"]
    )
    assert all(c["constraints"]["completed_after_tax_exit"] for c in result["candidates"])


def test_declining_retains_original_zero_account_and_clears_only_its_price_binding():
    profile = case()
    household, binding = compile_candidate(profile, [profile.dimensions[0].choices[-1]])
    assert household.accounts == profile.household.accounts
    assert household.drilling_plan is None and binding.drilling is None
    assert complete(household, dict(account_balances={"cash": 200000, "drilling": 0}))
