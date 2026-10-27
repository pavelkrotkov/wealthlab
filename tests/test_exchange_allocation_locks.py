"""Physical source restrictions prevent phantom proceeds and false liquid/closed-position labels."""

from datetime import date

import pytest
from exchange_allocation_cases import allocated

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.exchange_fund_example import request


@pytest.mark.parametrize("later_sale", [False, True])
def test_retained_only_source_lock_denies_now_and_only_an_explicit_later_order_can_sell(later_sale):
    data = allocated(0).model_dump(mode="json")
    plan = data["exchange_fund_plan"]
    plan["source_lot"]["liquid_after"] = "2026-07-01"
    plan["requests"] = [request("blocked", date(2026, 1, 31), "sell_source")]
    if later_sale:
        plan["requests"].append(request("later", date(2026, 7, 31), "sell_source"))
    rows = project(Scenario.model_validate(data))
    assert rows[0]["exchange_denied_source_sales"] == 1
    assert rows[0]["exchange_locked_value"] == 100000
    assert rows[0]["exchange_liquid_value"] == 0
    assert rows[0]["account_balances"]["exchange"] == 100000
    assert sum(row["exchange_source_sale_cash"] for row in rows) == (100000 if later_sale else 0)
    assert rows[-1]["exchange_positions_closed"] is later_sale


def test_market_lock_keeps_source_and_fund_capital_restricted_without_closure():
    data = allocated(400).model_dump(mode="json")
    data["exchange_fund_plan"]["observations"][-1]["locked"] = True
    final = project(Scenario.model_validate(data))[-1]
    assert final["exchange_denied_source_sales"] == 1
    assert final["exchange_locked_value"] == 100000
    assert final["exchange_liquid_value"] == 0
    assert final["exchange_positions_closed"] is False
    assert final["account_balances"]["exchange"] == 100000
