"""Even programmatically constructed inactive profiles must obey actual native amount bounds."""

from copy import deepcopy
from decimal import Decimal

import pytest
from optimization_drilling_cases import envelope, inputs, offer

from wealthlab.optimization.drilling_apply import apply


def test_source_confirmation_cannot_hide_negative_production_in_an_inactive_native_profile():
    household, offered, _, _ = inputs()
    original = household.drilling_plan
    negative = original.observations[0].model_copy(update={"production_units": Decimal(-1)})
    invalid = original.model_copy(update={"observations": [negative]})
    choices = [offered[0], offer("inactive_invalid", invalid)]
    confirmed, scope = envelope(household, choices)
    data = household.model_dump(mode="json")
    before = deepcopy(data)
    with pytest.raises(ValueError, match="production_units"):
        apply(data, choices, "well", confirmed, scope)
    assert data == before
