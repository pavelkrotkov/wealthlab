"""Sourced property observations share native market cash/taxes without invented factor exposure."""

import pytest

from wealthlab.household.projection import project
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.markets.property_example import synthetic


@pytest.mark.parametrize("mode", ["deterministic", "monte_carlo", "historical", "stress"])
def test_shared_paths_keep_property_marks_and_actual_close_separate_from_invented_returns(mode):
    household, market, binding = synthetic(mode)
    result = run(household, generate(market), binding, indices=[0])
    actual = result["details"][0]["rows"]
    baseline = project(household)
    assert actual[-1]["net_wealth"] == baseline[-1]["net_wealth"] == 246400
    assert actual[-1]["property_audit"] == baseline[-1]["property_audit"]
    assert result["outcomes"][0]["property_feasible"]
    assert result["outcomes"][0]["joint_feasible"]
    assert result["outcomes"][0]["issuer_concentration_complete"] is False
