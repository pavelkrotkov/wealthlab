"""Actual wages, taxes, final share sales and held-out replay conserve household capital."""

from decimal import Decimal

import pytest
from optimization_cases import flat

from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(flat())


def test_fully_liquidated_candidate_cash_identity_and_tax_diagnostic(result):
    early, later = result["candidates"]
    assert early["median_real_after_tax_exit_wealth"] == Decimal(251999)
    assert (
        later["median_real_after_tax_exit_wealth"] == Decimal(311999) - later["median_net_cash_tax"]
    )
    assert later["median_net_cash_tax"] > early["median_net_cash_tax"]
    assert result["selection"] == "candidate_1"
    assert result["global_optimum_claim"] is False


def test_selected_policy_replays_on_separate_sample_without_changing_policy(result):
    held = result["held_out"]
    assert held["selected_candidate"] == result["selection"]
    assert held["assessment"]["eligible"]
    assert held["batch"]["metadata"]["seed"] == 107
    assert result["training_batch"]["metadata"]["seed"] == 71
    assert held["batch"]["metadata"]["batch_id"] != result["training_batch"]["metadata"]["batch_id"]


def test_all_cash_exit_keeps_remaining_tax_position_in_the_audit(result):
    rows = result["held_out"]["results"]["details"][0]["rows"]
    assert rows[-1]["account_balances"]["brokerage"] == 0
    assert rows[-1]["net_wealth"] == rows[-1]["closing_cash"] - rows[-1]["tax_position"]
    assert result["held_out"]["results"]["binding"] == result["inputs"]["binding"]
