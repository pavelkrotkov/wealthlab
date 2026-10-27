"""Counterfactual starting shares cannot replace existing well ownership as a tax-free action."""

import pytest
from optimization_drilling_cases import envelope, inputs, offer

from wealthlab.household.scenario import Scenario
from wealthlab.optimization.drilling_profiles import validate_offers


def test_zero_opening_mode_change_still_requires_independent_no_prior_interest_confirmation():
    household, offered, _, _ = inputs()
    unconfirmed = offered[1].model_copy(
        update={"mode_change_no_prior_interest_or_obligations_confirmed": False}
    )
    record, scope = envelope(household, [unconfirmed])
    with pytest.raises(ValueError, match="independently confirmed no prior"):
        validate_offers(household, [unconfirmed], record, scope)


@pytest.mark.parametrize("component", ["opening_property_value", "opening_federal_basis"])
def test_existing_property_or_zero_value_tax_history_cannot_become_opening_reference_shares(
    component,
):
    household, _, _, _ = inputs()
    data = household.model_dump(mode="json")
    data["drilling_plan"][component] = "10000"
    if component == "opening_property_value":
        data["accounts"][1]["balance"] = "10000"
    original = Scenario.model_validate(data)
    assert original.drilling_plan is not None
    reference = original.drilling_plan.model_copy(update={"mode": "liquid_reference"})
    supplied = offer("not_an_actual_sale", reference, mode_change=True)
    record, scope = envelope(original, [supplied])
    with pytest.raises(ValueError, match="actual taxable transfer"):
        validate_offers(original, [supplied], record, scope)
