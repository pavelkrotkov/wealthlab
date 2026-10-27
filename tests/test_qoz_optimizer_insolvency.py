"""Entity-lender debt stays visible but cannot become household recourse on an actual stock exit."""

from copy import deepcopy

from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.optimization.qoz_exits import completed


def scenario(locked=False):
    data = flat().model_dump(mode="json")
    data["qoz_plan"]["economics"]["long_multiple"] = "2"
    observations = data["qoz_plan"]["observations"]
    observations[1]["asset_return"] = "-1"
    for row in observations[-2:]:
        row["locked"] = locked
    return Scenario.model_validate(data)


def test_actual_zero_proceeds_stock_sale_can_close_without_erasing_internal_debt():
    household = scenario()
    row = project(household)[-1]
    assert completed(household, row)
    assert row["qoz_audit"]["ending_entity"]["loan"] == 80000
    assert row["closing_cash"] == 25000
    assert row["qoz_audit"]["economic_state"]["sold"] is True


def test_zero_nav_but_unsold_locked_stock_interest_remains_open():
    household = scenario(locked=True)
    row = project(household)[-1]
    assert row["qoz_nav"] == 0 and row["account_balances"]["qoz"] == 0
    assert not completed(household, row)
    damaged = deepcopy(row)
    damaged["qoz_audit"]["economic_state"]["sold"] = True
    damaged["qoz_audit"]["ending_entity"]["loan"] = "-1"
    assert not completed(household, damaged)
