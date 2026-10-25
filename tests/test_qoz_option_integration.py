"""Separate option/QOZ books share actual receipts without sharing account ownership.

The $500 call premium reaches household cash before the $80k subscription.
The later $11k stock delivery plus that premium and $105k other opening
capital total $116,500 before actual annual taxes; no stock or loan is counted twice.
"""

from decimal import Decimal

import pytest
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.option_household_example import synthetic as option_example
from wealthlab.products.qoz_accounts import validate_account


def test_actual_option_cash_reaches_a_separate_qoz_subscription_and_one_annual_return():
    data = flat(2026).model_dump(mode="json")
    other = option_example().model_dump(mode="json")
    data["accounts"].append(other["accounts"][1])
    data["option_plan"] = other["option_plan"]
    rows = project(Scenario.model_validate(data))
    assert rows[0]["closing_cash"] == Decimal(25500)
    assert rows[0]["qoz_call_paid"] == Decimal(80000)
    final = rows[-1]
    assert final["annual_tax"]["federal"]["agi"] == Decimal(86500)
    assert final["annual_tax"]["new_jersey"]["total_income"] == Decimal(75500)
    assert final["net_wealth"] == Decimal(116500) - final["annual_tax"]["total_liability"]


def test_a_zero_opening_qoz_account_cannot_also_belong_to_an_option_plan():
    data = flat(2026).model_dump(mode="json")
    data["option_plan"] = option_example().option_plan.model_dump(mode="json")
    data["option_plan"]["account_id"] = "qoz"
    scenario = Scenario.model_validate(data)
    with pytest.raises(ValueError, match="share ownership"):
        validate_account(scenario, scenario.qoz_plan)
