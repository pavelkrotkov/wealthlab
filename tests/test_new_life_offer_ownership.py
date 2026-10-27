"""New accounts require a named owner and preserve the independent baseline insurance need."""

import pytest
from new_life_offer_cases import inputs

from wealthlab.household.scenario import Scenario
from wealthlab.optimization.new_life_offers import apply, validate_offers
from wealthlab.products.life_allocation_example import synthetic


def test_an_offer_cannot_create_an_insurance_need_when_the_baseline_has_none():
    household, offers = inputs()
    missing = household.model_copy(update={"life_plan": None})
    with pytest.raises(ValueError, match="baseline insurance-need plan"):
        validate_offers(missing, offers)
    data = missing.model_dump(mode="json")
    apply(data, [], [])
    assert data == missing.model_dump(mode="json")


def test_explicit_owner_is_preserved_when_two_members_have_the_same_birth_date():
    household, offers = inputs()
    data = household.model_dump(mode="json")
    data["members"][1]["birth_date"] = data["members"][0]["birth_date"]
    data["life_plan"]["insurance_need_by_owner"]["person_b"] = "250000"
    owner_b = offers[0].model_copy(update={"owner": "person_b"})
    apply(data, [owner_b], [owner_b.id])
    selected = Scenario.model_validate(data)
    assert selected.accounts[-1].owner == "person_b"
    assert data["life_plan"]["insurance_need_by_owner"] == {
        "person_a": "150000",
        "person_b": "250000",
    }


def test_an_additional_offer_preserves_all_existing_policy_accounts_and_paths():
    _, offers = inputs()
    baseline = synthetic().alternatives["new_issue"]
    extra = offers[0].model_copy(
        update={
            "holding": offers[0].holding.model_copy(update={"account_id": "another_new_policy"})
        }
    )
    data = baseline.model_dump(mode="json")
    apply(data, [extra], [extra.id])
    assert data["accounts"][:-1] == baseline.model_dump(mode="json")["accounts"]
    assert (
        data["life_plan"]["holdings"][:-1]
        == baseline.model_dump(mode="json")["life_plan"]["holdings"]
    )
    assert data["life_plan"]["insurance_need_by_owner"] == {"person_a": "150000"}
