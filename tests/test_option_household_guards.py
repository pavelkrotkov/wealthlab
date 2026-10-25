"""Conflicting books and unknown eligibility cannot enter a household spending result."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.option_household_example import synthetic


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("actual_household_cash_confirmed", False, "Confirm actual"),
        ("tax_history_and_no_duplicate_income_confirmed", False, "Confirm actual"),
    ],
)
def test_actual_cash_and_complete_tax_history_require_confirmation(field, value, message):
    data = synthetic().model_dump(mode="json")
    data["option_plan"][field] = value
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data))


@pytest.mark.parametrize(
    "field",
    [
        "federal_rules",
        "nj_rules",
        "straddle",
        "covered_call",
        "constructive_sale",
        "holding_period",
        "nj_premium_basis",
        "wash_sales",
    ],
)
def test_unresolved_option_rule_blocks_actual_household_tax(field):
    data = synthetic().model_dump(mode="json")
    data["option_plan"]["case"]["tax"][field] = "unresolved"
    with pytest.raises(ValueError, match="Resolve federal/NJ"):
        project(Scenario.model_validate(data))


def test_missing_monthly_quote_coverage_and_generated_market_binding_are_explicit_guards():
    data = synthetic().model_dump(mode="json")
    data["option_plan"]["case"]["marks"].pop(1)
    with pytest.raises(ValueError, match="Every household month"):
        project(Scenario.model_validate(data))
    from wealthlab.products.option_household import make

    with pytest.raises(ValueError, match="generated market binding"):
        make(synthetic(), object())


def test_future_mistyped_deferral_cannot_silently_allow_a_household_capital_loss():
    data = synthetic().model_dump(mode="json")
    case = data["option_plan"]["case"]
    case["tax"].update(straddle="supplied_deferrals", federal_deferrals={"unknown:future": "100"})
    with pytest.raises(ValueError, match="unmatched recognition ID"):
        project(Scenario.model_validate(data))


def test_mid_horizon_failed_physical_delivery_requires_resolution_before_continuing():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "500"
    data["option_plan"]["case"]["legs"][0].update(side="long", strike="100")
    with pytest.raises(ValueError, match="Pending expired physical delivery"):
        project(Scenario.model_validate(data))
