"""Whole-illustration selection is atomic; inactive invalid offers cannot hide in a menu."""

from copy import deepcopy

import pytest
from new_life_offer_cases import inputs

from wealthlab.optimization.new_life_offers import apply, validate_offers
from wealthlab.products.life_allocation_example import synthetic


@pytest.mark.parametrize("selected", [["unknown"], ["supplied_new_issue", "supplied_new_issue"]])
def test_unknown_or_duplicate_selections_leave_all_household_inputs_intact(selected):
    household, offers = inputs()
    data = household.model_dump(mode="json")
    before = deepcopy(data)
    with pytest.raises(ValueError, match="unique known"):
        apply(data, offers, selected)
    assert data == before


def test_alternate_whole_quotes_sharing_a_destination_are_valid_but_cannot_both_be_selected():
    household, offers = inputs()
    alternate = offers[0].model_copy(update={"id": "alternate_complete_quote"})
    validate_offers(household, [*offers, alternate])
    data = household.model_dump(mode="json")
    before = deepcopy(data)
    with pytest.raises(ValueError, match="destination are exclusive"):
        apply(data, [*offers, alternate], [offers[0].id, alternate.id])
    assert data == before


def test_invalid_inactive_quote_blocks_application_before_any_selected_account_is_added():
    household, offers = inputs()
    inactive = offers[0].model_copy(
        update={"id": "unconfirmed", "matched_new_issue_terms_confirmed": False}
    )
    data = household.model_dump(mode="json")
    before = deepcopy(data)
    with pytest.raises(ValueError, match="Confirm"):
        apply(data, [*offers, inactive], [offers[0].id])
    assert data == before


def test_even_a_zero_balance_existing_policy_cannot_be_replaced_with_a_new_offer():
    _, offers = inputs()
    existing = synthetic().alternatives["new_issue"]
    assert existing.accounts[-1].balance == 0
    with pytest.raises(ValueError, match="cannot replace"):
        validate_offers(existing, offers)


def test_duplicate_quote_identity_is_rejected_even_when_no_offer_will_be_selected():
    household, offers = inputs()
    with pytest.raises(ValueError, match="offer identifiers must be unique"):
        apply(household.model_dump(mode="json"), [*offers, offers[0]], [])
