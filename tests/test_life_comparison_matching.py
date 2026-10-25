"""Changing the household background cannot masquerade as an insurance strategy benefit."""

import pytest

from wealthlab.products.life_comparison import compare
from wealthlab.products.life_comparison_existing import synthetic as existing
from wealthlab.products.life_comparison_inputs import LifeComparison
from wealthlab.products.life_comparison_markets import synthetic


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("spending", "background"),
        ("capital", "capital"),
        ("need", "insurance needs"),
        ("prices", "observations"),
        ("unpriced", "independently"),
    ],
)
def test_unmatched_inputs_do_not_produce_a_false_strategy_difference(field, message):
    data = synthetic().model_dump(mode="json")
    alternative = data["alternatives"]["limited"]
    changes = {
        "spending": (alternative["expenses"][0], "monthly_amount", "999"),
        "capital": (alternative["accounts"][0], "balance", "9999"),
        "need": (alternative["life_plan"]["insurance_need_by_owner"], "person_a", "1"),
        "prices": (alternative["lot_plan"]["opening_prices"], "stock", "99"),
        "unpriced": (data, "independently_priced_protection_confirmed", False),
    }
    target, key, value = changes[field]
    target[key] = value
    with pytest.raises(ValueError, match=message):
        compare(LifeComparison.model_validate(data))


def test_reference_cannot_change_the_supplied_existing_surrender_settlement():
    data = existing().model_dump(mode="json")
    old = data["alternatives"]["liquid_term"]["life_plan"]["holdings"][0]
    old["contract"]["events"][0]["amount"] = "11000"
    with pytest.raises(ValueError, match="opening surrender"):
        compare(LifeComparison.model_validate(data))


def test_market_inputs_without_bindings_do_not_fall_back_to_entered_marks():
    data = synthetic("deterministic").model_dump(mode="json")
    data["binding"] = None
    with pytest.raises(ValueError, match="both shared market"):
        compare(LifeComparison.model_validate(data))
