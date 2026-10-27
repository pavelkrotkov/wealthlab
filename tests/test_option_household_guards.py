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


def test_future_mistyped_deferral_cannot_silently_allow_a_household_capital_loss():
    data = synthetic().model_dump(mode="json")
    case = data["option_plan"]["case"]
    case["tax"].update(straddle="supplied_deferrals", federal_deferrals={"unknown:future": "100"})
    with pytest.raises(ValueError, match="unmatched recognition ID"):
        project(Scenario.model_validate(data))
