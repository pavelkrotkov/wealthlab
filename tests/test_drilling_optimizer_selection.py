"""Invalid selections and inactive profiles cannot partially rewrite candidate inputs."""

from copy import deepcopy

import pytest
from optimization_drilling_cases import inputs

from wealthlab.optimization.drilling_apply import apply


def test_candidate_cannot_use_profile_selection_to_change_original_invested_account_capital():
    household, offers, confirmed, scope = inputs()
    data = household.model_dump(mode="json")
    data["accounts"][1]["balance"] = "1"
    before = deepcopy(data)
    with pytest.raises(ValueError, match="household account capital"):
        apply(data, offers, "well", confirmed, scope)
    assert data == before
