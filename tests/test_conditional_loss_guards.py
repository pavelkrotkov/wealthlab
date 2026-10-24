"""Unknown eligibility and inconsistent deferral dates cannot silently create deductions."""

import pytest
from conditional_loss_cases import allocation

from wealthlab.products.conditional_allocations import events
from wealthlab.products.household_inputs import SleeveAllocation
from wealthlab.products.loss_timing import LossTiming


@pytest.mark.parametrize(
    "treatment,date", [("allowed", "2027-01-01"), ("denied", "2027-01-01"), ("deferred", None)]
)
def test_release_date_must_match_conditional_treatment(treatment, date):
    with pytest.raises(ValueError, match="Only deferred"):
        LossTiming(treatment=treatment, release_on=date)


def test_unconfirmed_eligibility_cannot_become_an_allowed_loss():
    data = allocation().model_dump(mode="json")
    data["federal_loss"]["eligibility_after_limits_assumed"] = False
    with pytest.raises(ValueError, match="eligibility"):
        events(SleeveAllocation.model_validate(data))


def test_deferred_release_cannot_precede_original_allocation():
    with pytest.raises(ValueError, match="later"):
        events(allocation("deferred", release="2026-04-01"))
