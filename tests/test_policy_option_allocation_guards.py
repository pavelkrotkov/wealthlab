"""Inactive option offers cannot change ownership, risk facts or available source capital.

These are actual native/profile rejections before any candidate can trade. A
locked zero-unit choice does not make its malformed positive alternatives safe.
"""

import pytest
from optimization_cases import changed
from optimization_option_cases import case

from wealthlab.markets.paths import generate
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import evaluate
from wealthlab.optimization.validation import validate


def locked(edit):
    data = case().model_dump(mode="json")
    data["dimensions"][-1]["locked_choice"] = "cash"
    edit(data)
    return PolicySearch.model_validate(data)


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("cash_account", "missing", "existing USD cash"),
        ("owner", "person_a", "owner role"),
        ("provenance", "unresolved", "sourced"),
        ("opening_cash_purchase_assumed_confirmed", False, "sourced"),
        ("per_unit_absolute_fees_confirmed", False, "per allocation unit"),
        ("maximum_units", 1, "bounds"),
    ],
)
def test_locked_zero_does_not_hide_bad_source_owner_terms_or_positive_bounds(field, value, match):
    profile = locked(lambda d: d["option_opportunity"].update({field: value}))
    with pytest.raises(ValueError, match=match):
        validate(profile)


@pytest.mark.parametrize("count", [True, 1.5, -1, 100001])
def test_contract_quantity_is_a_strict_bounded_integer(count):
    with pytest.raises(ValueError):
        locked(lambda d: d["dimensions"][-1]["choices"][1].update(option_units=count))


def test_a_positive_choice_cannot_execute_without_its_fixed_opportunity():
    profile = changed(case(), lambda d: d.update(option_opportunity=None))
    with pytest.raises(ValueError, match="supplied opportunity"):
        validate(profile)


def test_an_empty_or_reversed_offer_menu_is_rejected_before_search():
    with pytest.raises(ValueError, match="Minimum option units"):
        locked(lambda d: d["option_opportunity"].update(minimum_units=6))
    profile = changed(case(), lambda d: d.update(dimensions=d["dimensions"][:1]))
    with pytest.raises(ValueError, match="bounds"):
        validate(profile)


def test_the_new_destination_cannot_take_over_an_existing_household_account():
    def edit(data):
        data["household"]["accounts"].append(dict(data["household"]["accounts"][1], id="options"))

    with pytest.raises(ValueError, match="distinct destination"):
        validate(locked(edit))


def test_combined_purchase_capacity_uses_actual_source_cash_instead_of_a_new_reserve():
    profile = changed(case(), lambda d: d["household"]["accounts"][0].update(balance="10000"))
    candidate, result = evaluate(
        profile,
        [profile.dimensions[0].choices[0], profile.dimensions[-1].choices[1]],
        0,
        generate(profile.training),
    )
    assert result is None and not candidate["eligible"]
    assert "exceed available source cash" in candidate["unsupported_reason"]


def test_two_dimensions_cannot_both_control_the_same_option_book():
    profile = changed(
        case(), lambda d: d["dimensions"].append(dict(d["dimensions"][-1], id="second"))
    )
    with pytest.raises(ValueError, match="same policy"):
        validate(profile)


def test_an_existing_option_book_is_not_replaced_even_by_a_locked_zero_purchase():
    def edit(data):
        offer = data["option_opportunity"]
        data["household"]["option_plan"] = offer["unit"]
        data["binding"]["options"] = offer["binding"]

    with pytest.raises(ValueError, match="replace an existing option book"):
        validate(locked(edit))
