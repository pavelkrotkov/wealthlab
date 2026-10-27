"""A matching source hash cannot authorize replacement capital or altered unit/legal terms."""

import pytest
from optimization_drilling_cases import envelope, inputs, offer

from wealthlab.household.scenario import Scenario
from wealthlab.optimization.drilling_profiles import validate_offers
from wealthlab.products.drilling_inputs import DrillingPlan


@pytest.mark.parametrize(
    "field,value",
    [
        ("account_id", "another"),
        ("opening_federal_basis", "1"),
        ("household_recourse_for_modeled_creditors", False),
        ("legal_form", "limited_partner"),
    ],
)
def test_profile_cannot_change_original_account_capital_or_legal_liability_terms(field, value):
    household, _, _, _ = inputs()
    data = household.drilling_plan.model_dump(mode="json")
    data[field] = value
    plan = DrillingPlan.model_validate(data)
    offered = [offer("altered", plan)]
    confirmed, scope = envelope(household, offered)
    with pytest.raises(ValueError, match="Preserve original"):
        validate_offers(household, offered, confirmed, scope)


@pytest.mark.parametrize(
    "field,value",
    [
        ("commodity_price", "99"),
        ("royalty_fraction", "0.1"),
        ("reference_price", "99"),
        ("reference_locked", True),
        ("exit_requested", False),
    ],
)
def test_profile_unit_prices_royalties_and_dealing_calendar_stay_fixed(field, value):
    household, _, _, _ = inputs()
    data = household.drilling_plan.model_dump(mode="json")
    data["observations"][0][field] = value
    offered = [offer("altered", DrillingPlan.model_validate(data))]
    confirmed, scope = envelope(household, offered)
    with pytest.raises(ValueError, match="per-unit"):
        validate_offers(household, offered, confirmed, scope)


@pytest.mark.parametrize(
    "field",
    [
        "opening_cash",
        "opening_property_value",
        "opening_federal_basis",
        "opening_nj_basis",
        "opening_at_risk",
        "opening_federal_tangible_basis",
        "opening_nj_tangible_basis",
    ],
)
def test_no_entry_cannot_erase_any_prior_cash_property_basis_or_at_risk(field):
    household, offers, _, _ = inputs()
    data = household.model_dump(mode="json")
    data["drilling_plan"][field] = "1"
    if field in {"opening_cash", "opening_property_value"}:
        data["accounts"][1]["balance"] = "1"
    original = Scenario.model_validate(data)
    offered = [offers[-1]]
    confirmed, scope = envelope(original, offered)
    with pytest.raises(ValueError, match="No-entry cannot erase"):
        validate_offers(original, offered, confirmed, scope)
