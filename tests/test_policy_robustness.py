"""Actual paired households expose blocked exits and scenario risk without reselection."""

from copy import deepcopy

import pytest
from optimization_robustness_cases import case

from wealthlab.optimization.robustness import validation_passed
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_required_liquidity_failure_does_not_replace_training_selected_policy(result):
    assert result["selection"] == "candidate_1"
    assert result["held_out"]["assessment"]["eligible"]
    assert not result["configured_validation_passed"]
    locked = result["robustness"]["exit_lock"]
    assert locked["status"] == "failed"
    assert "completed_after_tax_exit" in locked["selected"]["assessment"]["unmet_constraints"]


def test_baseline_and_selected_share_exact_paths_in_each_independent_check(result):
    """The original baseline already retires at the winning later date.

    Paired differences must therefore be zero even under different scenarios;
    otherwise the comparison has changed inputs or assigned different paths.
    """
    for check in result["robustness"].values():
        assert check["selected_candidate"] == result["selection"]
        assert check["baseline"]["results"]["batch_id"] == check["batch"]["metadata"]["batch_id"]
        assert check["selected"]["results"]["batch_id"] == check["batch"]["metadata"]["batch_id"]
        assert all(p["real_wealth_change"] == 0 for p in check["paired_changes"])


def test_supplied_paths_have_no_sampling_probability_or_wilson_interval(result):
    for check in result["robustness"].values():
        assessment = check["selected"]["assessment"]
        assert check["sampling_scope"] == "supplied_path"
        assert assessment["joint_success_95_wilson"] is None
        assert assessment["reserve_success_95_wilson"] is None


def test_optional_failure_remains_reported_but_is_not_a_required_validation_gate(result):
    checks = deepcopy(result["robustness"])
    checks["exit_lock"]["required"] = False
    assert validation_passed(result["held_out"], checks)
    assert checks["exit_lock"]["status"] == "failed"
