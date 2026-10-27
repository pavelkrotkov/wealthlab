"""QOF subscriptions and no-entry share one realized source sale and the same original capital."""

import pytest
from optimization_qoz_cases import case

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_source_proceeds_and_completed_stock_settlement_are_not_counted_twice(result):
    candidates = result["candidates"]
    assert all(c["eligible"] for c in candidates), candidates
    # 68000taxable uses the68000-68050table midpoint:1246.6125 rounds to1247.
    assert [c["median_real_after_tax_exit_wealth"] for c in candidates] == [103753] * 4
    assert {c["opening_allocation_audit"]["allocated_opening_wealth"] for c in candidates} == {
        105000
    }
    assert result["configured_validation_passed"]
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 103753


def test_no_entry_retains_the_same_source_and_original_zero_account():
    profile = case()
    household, binding = compile_candidate(profile, [profile.dimensions[0].choices[0]])
    assert household.qoz_plan is None and binding.qoz is None
    assert household.accounts == profile.household.accounts
    assert household.lot_plan == profile.household.lot_plan


def test_reference_is_structurally_ineligible_for_qoz_tax_deferral():
    profile = case()
    household, _ = compile_candidate(profile, [profile.dimensions[0].choices[-1]])
    assert household.qoz_plan.federal == household.qoz_plan.new_jersey == "denied"
    assert household.qoz_plan.settlement_months == 0
