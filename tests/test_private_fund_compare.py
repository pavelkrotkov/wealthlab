"""Matched public synthetic scenarios use one realized batch and the actual household consumer."""

import pytest

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.products.private_fund_compare import compare
from wealthlab.products.private_fund_example import synthetic


def run(data):
    return compare(
        Scenario.model_validate(data["fund"]),
        Scenario.model_validate(data["reference"]),
        generate(MarketCase.model_validate(data["market"])),
        HouseholdBinding.model_validate(data["binding"]),
        indices=[0],
    )


@pytest.mark.parametrize("mode", ["deterministic", "monte_carlo", "historical", "stress"])
def test_all_modes_share_actual_paths_and_preserve_conditional_unsettled_exit(mode):
    result = run(synthetic(mode))
    assert result["fund"]["batch_id"] == result["reference"]["batch_id"]
    assert result["exit_status"] == [
        dict(path=0, fund_complete=False, reference_complete=True, both_fully_cash_liquidated=False)
    ]
    assert result["fund"]["details"][0]["rows"][-1]["sleeve_audit"][-1]["fund_receivable"] > 0
    assert result["differences"][0]["real_wealth_change"] != 0


def test_changed_household_background_is_not_a_paired_product_comparison():
    data = synthetic()
    data["reference"]["accounts"][0]["balance"] = "1"
    with pytest.raises(ValueError, match="identical household capital"):
        run(data)


def test_leveraged_reference_is_rejected():
    data = synthetic()
    data["reference"]["sleeve_plan"]["sleeves"][0]["case"]["long_multiple"] = "1.1"
    with pytest.raises(ValueError, match="unlevered reference"):
        run(data)
