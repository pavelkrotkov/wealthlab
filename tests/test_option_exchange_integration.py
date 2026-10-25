"""Prepared integration checks; apply after the coordinated options/main rebase."""

import pytest

from tests.option_exchange_cases import combined, overlapping
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.exchange_fund_validation import validate as validate_exchange
from wealthlab.products.option_household_validation import validate as validate_options


@pytest.mark.parametrize("owner", ["options", "exchange"])
def test_each_owner_rejects_the_same_option_exchange_account(owner):
    scenario = overlapping()
    with pytest.raises(ValueError, match="Options and exchange funds cannot share"):
        if owner == "options":
            validate_options(scenario, None)
        else:
            validate_exchange(scenario)


def test_distinct_books_conserve_capital_and_leave_cash_spending_unchanged():
    rows = project(Scenario.model_validate(combined()))
    final = rows[-1]
    assert final["closing_cash"] == 6500
    assert final["account_balances"]["options"] == 0
    assert final["account_balances"]["exchange"] > 0
    assert final["net_wealth"] == final["closing_cash"] + final["account_balances"]["exchange"]


def test_exchange_receipt_cannot_retroactively_fund_earlier_option_collateral():
    data = combined()
    data["option_plan"]["case"].update(cover_stock_calls=False, short_collateral_fraction="0.5")
    observation = data["exchange_fund_plan"]["observations"][0]
    observation["distribution"] = "2000"
    observation["allocation"].update(
        federal=dict(interest="2000"), new_jersey=dict(interest="2000")
    )
    first = project(Scenario.model_validate(data))[0]
    assert first["option_margin_unfunded"] > 0
    assert first["closing_cash"] == 1500
    assert first["essential_unfunded"] == 0
