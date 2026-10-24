"""Locked value survives; fixed outgoing requests cannot borrow a later return."""

from decimal import Decimal

from tests.wrapper_market_cases import flat, lock
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


def test_an_earlier_withdrawal_cannot_spend_the_later_month_end_gain():
    case, market, binding = flat()
    data = case.model_dump(mode="json")
    data["ira_plan"]["orders"] = [
        dict(
            id="early_draw",
            provenance="illustration",
            date="2026-01-01",
            source="retirement",
            destination=None,
            kind="withdrawal",
            amount="200000",
            early_penalty_exception=False,
        )
    ]
    rows = run(Scenario.model_validate(data), generate(market), binding)["details"][0]["rows"]
    order = rows[-1]["ira_annual_reconciliation"]["orders"][0]
    assert order["paid"] == 100000
    assert order["unfilled"] == 100000
    assert rows[-1]["account_balances"]["retirement"] == 0


def test_locked_ira_cannot_fund_real_spending_or_a_conversion_but_keeps_returns():
    case, market, binding = flat()
    data = case.model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["expenses"] = [
        dict(
            id="living",
            provenance="illustration",
            start=data["start"],
            end=data["end"],
            monthly_amount="1000",
            currency="USD",
            annual_growth=0,
            category="essential",
        )
    ]
    data["ira_plan"]["orders"] = [
        dict(
            id="draw",
            provenance="illustration",
            date="2026-01-01",
            source="retirement",
            destination=None,
            kind="withdrawal",
            amount="12000",
            early_penalty_exception=False,
        ),
        dict(
            id="convert",
            provenance="illustration",
            date="2026-07-01",
            source="retirement",
            destination="roth",
            kind="conversion",
            amount="10000",
            early_penalty_exception=False,
        ),
    ]
    result = run(Scenario.model_validate(data), generate(lock(market)), binding)
    rows = result["details"][0]["rows"]
    orders = rows[-1]["ira_annual_reconciliation"]["orders"]
    assert all(o["paid"] == 0 and o["blocked_by_liquidity"] for o in orders)
    assert rows[-1]["account_balances"]["retirement"] == Decimal("126824.17")
    assert result["outcomes"][0]["first_failure"] == "2026-01-01"
    assert sum(r["essential_unfunded"] for r in rows) == 12000
