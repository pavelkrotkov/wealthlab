"""Editable complete paths are visible in the native optimizer and compose with other starters.

The synthetic example keeps the user's default horizon and concentration checks.
A separate short flat case uses explicit test targets to prove actual execution.
"""

import pytest
from optimization_life_cases import case

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.life_example import extend


def test_illustrative_paths_are_not_added_to_private_households():
    data = case().model_dump(mode="json")
    data["household"]["synthetic"] = False
    with pytest.raises(ValueError, match="only extends synthetic"):
        extend(PolicySearch.model_validate(data))
