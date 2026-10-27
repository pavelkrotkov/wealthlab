"""Unknown eligibility and inconsistent deferral dates cannot silently create deductions."""

import pytest
from conditional_loss_cases import allocation

from wealthlab.products.conditional_allocations import events
from wealthlab.products.household_inputs import SleeveAllocation


def test_unconfirmed_eligibility_cannot_become_an_allowed_loss():
    data = allocation().model_dump(mode="json")
    data["federal_loss"]["eligibility_after_limits_assumed"] = False
    with pytest.raises(ValueError, match="eligibility"):
        events(SleeveAllocation.model_validate(data))


def test_deferred_release_cannot_precede_original_allocation():
    with pytest.raises(ValueError, match="later"):
        events(allocation("deferred", release="2026-04-01"))
