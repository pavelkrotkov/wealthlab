"""A comparison cannot fabricate starting basis or a cash payout from term lapse."""

import pytest

from wealthlab.products.life_comparison_example import synthetic
from wealthlab.products.life_comparison_inputs import LifeComparison
from wealthlab.products.life_comparison_validation import validate


def test_existing_policy_tax_history_cannot_appear_in_only_one_alternative():
    data = synthetic().model_dump(mode="json")
    data["alternatives"]["limited"]["life_plan"]["holdings"][0]["contract"][
        "opening_federal_basis"
    ] = "500"
    with pytest.raises(ValueError, match="opening policy history"):
        validate(LifeComparison.model_validate(data))


def test_term_failure_cannot_create_a_cash_settlement_from_zero_value_cover():
    data = synthetic().model_dump(mode="json")
    term = data["alternatives"]["liquid_term"]["life_plan"]["holdings"][0]
    term["failure_exits"]["term_2026_1"]["event"]["amount"] = "500"
    with pytest.raises(ValueError, match="term failure"):
        validate(LifeComparison.model_validate(data))
