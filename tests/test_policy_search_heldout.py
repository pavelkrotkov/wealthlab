"""Validation may reject a frozen winner, but must never become a second selection sample."""

from copy import deepcopy

import pytest
from optimization_cases import flat

from wealthlab.optimization import search as module
from wealthlab.optimization.assessment import score


def test_spending_safety_precedes_a_larger_after_tax_estate():
    safe = dict(joint_success_fraction=1, median_real_after_tax_exit_wealth=100)
    richer = dict(joint_success_fraction=0.95, median_real_after_tax_exit_wealth=1000000)
    assert score(safe) > score(richer)


@pytest.mark.parametrize("unsupported", [False, True])
def test_heldout_failure_preserves_training_winner_without_testing_runner_up(
    monkeypatch, unsupported
):
    case = flat()
    real_run = module.run
    observed = []

    def changed_run(household, batch, binding):
        seed = batch.metadata["seed"]
        observed.append(seed)
        if seed == case.validation.seed and unsupported:
            raise ValueError("Unsupported held-out execution")
        result = real_run(household, batch, binding)
        if seed == case.validation.seed:
            result = deepcopy(result)
            result["outcomes"][0]["joint_feasible"] = False
        return result

    monkeypatch.setattr(module, "run", changed_run)
    result = module.search(case)
    assert observed == [71, 71, 107]
    assert result["selection"] == "candidate_1"
    assert result["held_out"]["selected_candidate"] == "candidate_1"
    assert not result["held_out"]["assessment"]["eligible"]
