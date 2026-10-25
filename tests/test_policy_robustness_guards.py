"""Every named check preserves horizon, factors and return semantics before projecting."""

import pytest
from optimization_cases import changed
from optimization_robustness_cases import case

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.robustness import check_all, validation_passed
from wealthlab.optimization.validation import validate


@pytest.mark.parametrize(
    "mutation,message",
    [
        (lambda d: d["robustness"]["flat"]["market"].update(mode="monte_carlo"), "mode"),
        (lambda d: d["robustness"]["flat"]["market"].update(end="2029-01-01"), "horizon"),
        (
            lambda d: d["robustness"]["flat"]["market"]["assets"][0].update(id="different"),
            "factors",
        ),
        (
            lambda d: d["robustness"]["flat"]["market"].update(
                return_convention="total_return_reinvested"
            ),
            "convention",
        ),
    ],
)
def test_incomparable_checks_fail_before_search(mutation, message):
    with pytest.raises(ValueError, match=message):
        validate(changed(case(), mutation))


def test_budget_counts_both_policies_in_every_check():
    data = case().model_dump(mode="json")
    data["maximum_projection_months"] = 24 * (2 + 1 + 2 * 4) - 1
    with pytest.raises(ValueError, match="budget"):
        validate(PolicySearch.model_validate(data))


def test_unselected_search_explicitly_records_checks_not_run():
    checks = check_all(case(), None)
    assert {c["status"] for c in checks.values()} == {"not_run_no_training_candidate"}
    assert validation_passed(None, checks) is None
