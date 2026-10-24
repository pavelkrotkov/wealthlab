"""Household policies cannot acquire unmodeled quote timing or forecast tax budgets."""

import pytest

from tests.household_policy_cases import targets
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


@pytest.mark.parametrize(
    "updates, message",
    [
        (dict(date="2026-01-15"), "month-end decision dates"),
        (dict(mode="tax_budget", fraction=None, tax_budget="1000"), "annual-forecast adapter"),
    ],
)
def test_unsupported_decision_profiles_block_before_execution(updates, message):
    case, market, binding = targets()
    data = case.model_dump(mode="json")
    data["lot_plan"]["case"]["sale_policies"][0].update(updates)
    with pytest.raises(ValueError, match=message):
        run(Scenario.model_validate(data), generate(market), binding)


def test_market_lock_blocks_a_sale_policy_without_deleting_its_value():
    case, market, binding = targets()
    data = market.model_dump(mode="json")
    data.update(mode="stress", shocks=[dict(name="lock", month=0, lock_months=dict(equities=24))])
    rows = run(case, generate(MarketCase.model_validate(data)), binding)["details"][0]["rows"]
    decisions = rows[-1]["lot_audit"]["sale_decisions"]
    assert all(d["sold_units"] == 0 for d in decisions)
    assert all(d["status"] == "blocked by market liquidity lock" for d in decisions)
    assert rows[-1]["account_balances"]["brokerage"] == 100000
