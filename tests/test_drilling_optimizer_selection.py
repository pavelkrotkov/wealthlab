"""Invalid selections and inactive profiles cannot partially rewrite candidate inputs."""

from copy import deepcopy

import pytest
from optimization_drilling_cases import envelope, inputs

from wealthlab.optimization.drilling_apply import apply


def test_unknown_selection_is_atomic_after_every_inactive_profile_is_validated():
    household, offers, confirmed, scope = inputs()
    data = household.model_dump(mode="json")
    before = deepcopy(data)
    with pytest.raises(ValueError, match="known complete drilling"):
        apply(data, offers, "missing", confirmed, scope)
    assert data == before


def test_invalid_inactive_quote_blocks_selection_before_any_candidate_input_mutation():
    household, offers, _, _ = inputs()
    offers[-1] = offers[-1].model_copy(update={"complete_matched_terms_confirmed": False})
    confirmed, scope = envelope(household, offers)
    data = household.model_dump(mode="json")
    before = deepcopy(data)
    with pytest.raises(ValueError, match="Every drilling offer"):
        apply(data, offers, "well", confirmed, scope)
    assert data == before


def test_candidate_cannot_use_profile_selection_to_change_original_invested_account_capital():
    household, offers, confirmed, scope = inputs()
    data = household.model_dump(mode="json")
    data["accounts"][1]["balance"] = "1"
    before = deepcopy(data)
    with pytest.raises(ValueError, match="household account capital"):
        apply(data, offers, "well", confirmed, scope)
    assert data == before
