"""Supplied cum-dividend stock terms do not manufacture return on a same-day call.

Two $50k subscriptions share a $10k declared dividend: each receives $5k and
retains $45k stock NAV. With $5k outside cash, wealth stays $105k before tax.
The supplied E&P dividend and eventual $10k stock loss keep distinct tax character.
"""

from decimal import Decimal

import pytest
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


@pytest.fixture(scope="module")
def rows():
    data = flat().model_dump(mode="json")
    plan = data["qoz_plan"]
    plan.update(federal="denied", new_jersey="denied")
    data["lot_plan"]["case"]["lots"][0].update(federal_basis="100000", nj_basis="100000")
    plan["calls"][0]["amount"] = "50000"
    plan["calls"].append(dict(plan["calls"][0], id="second", date="2027-02-28"))
    plan["observations"][1]["dividend_fraction_of_nav"] = ".10"
    return project(Scenario.model_validate(data))


def test_same_day_entitlement_conserves_dividend_cash_and_remaining_stock_value(rows):
    february = rows[1]
    assert february["qoz_dividends"] == Decimal(10000)
    assert february["closing_cash"] == Decimal(15000)
    assert february["qoz_nav"] == Decimal(90000)
    assert february["net_wealth"] == Decimal(105000)
    assert [t["dividends"] for t in rows[-1]["qoz_audit"]["tranches"]] == [5000, 5000]


def test_declared_ep_dividend_and_stock_loss_retain_distinct_annual_tax_character(rows):
    final = rows[-1]
    assert final["annual_tax"]["federal"]["agi"] == Decimal(7000)
    assert final["annual_tax"]["new_jersey"]["total_income"] == Decimal(10000)
    assert final["net_wealth"] == Decimal(105000) - final["annual_tax"]["total_liability"]


def test_unknown_subscription_dividend_entitlement_blocks_the_contract():
    data = flat().model_dump(mode="json")
    data["qoz_plan"]["subscriptions_share_same_day_dividends_assumed_confirmed"] = False
    with pytest.raises(ValueError, match="contract assumptions"):
        project(Scenario.model_validate(data))
