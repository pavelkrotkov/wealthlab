"""Locked/no-purchase choices cannot hide invalid source quotes or change coverage requirements."""

import pytest
from optimization_cases import changed
from optimization_new_life_cases import case

from wealthlab.optimization.new_life_example import extend
from wealthlab.optimization.search import search
from wealthlab.optimization.validation import validate


def test_every_inactive_quote_needs_an_available_substantive_source():
    def edit(data):
        data["dimensions"][-1]["locked_choice"] = "no_new_policy"
        data["new_life_opportunities"][0]["source"] = " " * 20

    with pytest.raises(ValueError, match="independently sourced"):
        validate(changed(case(), edit))


def test_an_unknown_whole_illustration_is_not_a_new_policy_quantity_or_interpolation():
    profile = changed(
        case(), lambda d: d["dimensions"][-1]["choices"][1].update(new_life_purchases=["unknown"])
    )
    with pytest.raises(ValueError, match="known new-life"):
        validate(profile)


def test_independent_positive_protection_need_prevents_surrender_from_ranking_as_safe():
    profile = changed(
        case(),
        lambda d: d["household"]["life_plan"].update(
            insurance_need_by_owner=dict(person_a="50000")
        ),
    )
    result = search(profile)
    assert result["selection"] is None
    assert all(not c["constraints"]["spending_and_product_safety"] for c in result["candidates"])
    assert profile.household.life_plan.insurance_need_by_owner["person_a"] == 50000


def test_private_inputs_and_preexisting_source_offers_are_never_replaced_by_a_starter():
    with pytest.raises(ValueError, match="replace existing"):
        extend(case())
    private = changed(case(), lambda d: d["household"].update(synthetic=False))
    with pytest.raises(ValueError, match="only extends synthetic"):
        extend(private)
