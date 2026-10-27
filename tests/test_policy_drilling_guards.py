"""An edit invalidates the confirmed scope; inactive source facts remain binding."""

import pytest
from optimization_drilling_search_cases import case, changed

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.validation import validate


def test_changed_candidate_market_assumption_invalidates_the_independent_envelope():
    profile = changed(case(), lambda d: d["targets"].update(reserve_years=1), reconfirm=False)
    with pytest.raises(ValueError, match="new independently sourced envelope"):
        validate(profile)


def test_invalid_locked_out_profile_cannot_be_hidden_by_selecting_no_entry():
    def edit(data):
        data["dimensions"][0]["locked_choice"] = "no_entry"
        data["drilling_offers"][0]["complete_matched_terms_confirmed"] = False

    with pytest.raises(ValueError, match="Every drilling offer"):
        validate(changed(case(), edit))


def test_unknown_selection_fails_before_a_candidate_can_run():
    profile = changed(
        case(), lambda d: d["dimensions"][0]["choices"][0].update(drilling_offer="missing")
    )
    with pytest.raises(ValueError, match="complete supplied offer"):
        validate(profile)


def test_duplicate_controllers_cannot_overwrite_the_original_drilling_selection():
    def edit(data):
        data["dimensions"].append(
            dict(id="duplicate", choices=[dict(id="cash", drilling_offer="no_entry")])
        )

    profile = changed(case(), edit)
    with pytest.raises(ValueError, match="Different dimensions"):
        validate(profile)
    with pytest.raises(ValueError, match="Only one dimension"):
        compile_candidate(profile, [d.choices[0] for d in profile.dimensions])


def test_drilling_plan_without_complete_envelope_is_not_optimizer_eligible():
    profile = case().model_copy(update={"drilling_envelope": None})
    with pytest.raises(ValueError, match="independent drilling envelope"):
        validate(profile)
