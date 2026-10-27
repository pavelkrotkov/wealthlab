"""Original educational offers cannot overwrite source accounts or extend their quoted horizon."""

import pytest
from optimization_cases import flat

from wealthlab.optimization.drilling_example import extend
from wealthlab.optimization.inputs import PolicySearch


@pytest.mark.parametrize(
    "change,message",
    [
        ("private", "synthetic"),
        ("existing", "existing plan"),
        ("calendar", "two-year"),
        ("account", "existing account"),
    ],
)
def test_starter_keeps_original_source_and_calendar(change, message):
    profile = flat()
    data = profile.model_dump(mode="json")
    if change == "private":
        data["household"]["synthetic"] = False
    if change == "existing":
        profile = extend(profile)
        data = profile.model_dump(mode="json")
    if change == "calendar":
        data["household"]["end"] = "2027-12-01"
    if change == "account":
        data["household"]["accounts"][1]["id"] = "drilling"
        data["household"]["lot_plan"] = None
    with pytest.raises(ValueError, match=message):
        extend(PolicySearch.model_validate(data))
