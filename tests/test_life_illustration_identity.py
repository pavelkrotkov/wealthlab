"""Stable identity prevents merging unrelated policy schedules or dated values."""

from copy import deepcopy

import pytest

from tests.test_life_illustration_cash import study
from wealthlab.products.life_illustration_inputs import LifeStudy


def test_duplicate_policy_or_flow_ids_and_value_dates_are_rejected():
    data = study().model_dump(mode="json")
    duplicate = deepcopy(data)
    duplicate["illustrations"].append(deepcopy(duplicate["illustrations"][0]))
    with pytest.raises(ValueError, match="Illustration IDs"):
        LifeStudy.model_validate(duplicate)
    data["illustrations"][0]["flows"] *= 2
    with pytest.raises(ValueError, match="Cash-flow IDs"):
        LifeStudy.model_validate(data)
    data = study().model_dump(mode="json")
    data["illustrations"][0]["values"] *= 2
    with pytest.raises(ValueError, match="unique/ordered"):
        LifeStudy.model_validate(data)
