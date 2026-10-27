"""New policy capital and historical contract rights cannot be fabricated as an allocation."""

import pytest
from new_life_offer_cases import inputs, offer_changed

from wealthlab.optimization.new_life_offers import validate_offers


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("opening_values", "gross_cash_value", "1"),
        ("opening_values", "gross_surrender_value", "1"),
        ("opening_values", "gross_death_benefit", "1"),
        ("contract", "opening_federal_basis", "1"),
        ("contract", "opening_federal_basis", None),
        ("contract", "opening_loan", "1"),
    ],
)
def test_every_inactive_offer_must_have_genuinely_zero_known_opening_components(
    section, field, value
):
    household, _ = inputs()
    offer = offer_changed(lambda data: data["holding"][section].update({field: value}))
    with pytest.raises(ValueError, match="zero opening"):
        validate_offers(household, [offer])


def test_historical_issue_date_cannot_masquerade_as_new_zero_cost_contract():
    household, _ = inputs()
    offer = offer_changed(lambda data: data["holding"]["contract"].update(issue_date="2025-01-01"))
    with pytest.raises(ValueError, match="issue dates must match"):
        validate_offers(household, [offer])


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("provenance", "unresolved", "Confirm"),
        ("matched_new_issue_terms_confirmed", False, "Confirm"),
        ("owner", "unknown", "independent baseline need"),
    ],
)
def test_unresolved_new_issue_terms_and_missing_owner_need_block_even_inactive_offers(
    field, value, message
):
    household, _ = inputs()
    offer = offer_changed(lambda data: data.update({field: value}))
    with pytest.raises(ValueError, match=message):
        validate_offers(household, [offer])


def test_a_future_quote_cannot_be_selected_using_hindsight_at_household_opening():
    household, _ = inputs()
    offer = offer_changed(lambda data: data["holding"]["contract"].update(source_date="2026-01-02"))
    with pytest.raises(ValueError, match="source must be available"):
        validate_offers(household, [offer])
