"""Inactive offers and future recognition require independent support, not a source hash alone."""

from datetime import date

import pytest
from optimization_drilling_cases import envelope, inputs, offer

from wealthlab.household.projection import project
from wealthlab.optimization.drilling_exits import completed
from wealthlab.optimization.drilling_profiles import validate_offers
from wealthlab.products.drilling_inputs import DrillingPlan


@pytest.mark.parametrize("actual", [True, False])
def test_interest_and_declined_status_cannot_be_simultaneously_assumed_or_omitted(actual):
    household, offered, _, _ = inputs()
    original = offered[0] if actual else offered[-1]
    contradictory = original.model_copy(
        update={"declined_no_prior_interest_or_obligations_confirmed": actual}
    )
    confirmed, scope = envelope(household, [contradictory])
    with pytest.raises(ValueError, match=r"also be a declined|Confirm no prior"):
        validate_offers(household, [contradictory], confirmed, scope)


def test_source_envelope_must_cover_future_release_even_after_the_property_is_sold():
    household, _, _, _ = inputs()
    data = household.drilling_plan.model_dump(mode="json")
    for item in data["observations"][0]["deductions"]:
        item["federal_timing"] = dict(
            treatment="deferred", release_on="2026-03-31", eligibility_after_limits_assumed=True
        )
    supplied = offer("future_recognition", DrillingPlan.model_validate(data))
    confirmed, scope = envelope(household, [supplied])
    with pytest.raises(ValueError, match="every supplied release date"):
        validate_offers(household, [supplied], confirmed, scope)
    extended = confirmed.model_copy(update={"valid_through": date(2026, 3, 31)})
    validate_offers(household, [supplied], extended, scope)
    case = household.model_copy(update={"drilling_plan": supplied.plan})
    row = project(case)[-1]
    assert row["drilling_audit"]["terminal_state"]["closed"] is True
    assert completed(case, row) is False
