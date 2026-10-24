"""Opening-notional costs and actual turnover reduce economic wealth once."""

from decimal import Decimal

from long_short_cases import batch, flat

from wealthlab.markets.inputs import MarketCase
from wealthlab.products.long_short_run import run


def test_dividends_borrow_financing_and_manager_costs_reconcile():
    case, market = flat(
        annual_borrow_rate=".12", annual_financing_rate=".12", annual_manager_fee=".12"
    )
    data = market.model_dump(mode="json")
    for asset in data["assets"]:
        asset["annual_cash_yield"] = 0.12
    row = run(case, batch(MarketCase.model_validate(data)))["details"][0]["rows"][0]
    assert (row["long_cash_yield"], row["short_dividend_cost"]) == (1300, 300)
    assert (row["borrow_cost"], row["financing_cost"], row["manager_fee"]) == (300, 300, 1000)
    assert row["investor_wealth"] == 109400


def test_rebalancing_reports_actual_turnover_and_post_cost_leverage():
    case, market = flat(turnover_cost=".01", rebalance="monthly", exit_at_horizon=False)
    data = market.model_dump(mode="json")
    data["assets"][0]["expected_annual_mark_return"] = 1.01**12 - 1
    row = run(case, batch(MarketCase.model_validate(data)))["details"][0]["rows"][0]
    assert row["entry_cost"] == 1600
    assert row["turnover_notional"] == 1780
    assert row["turnover_cost"] == Decimal("17.80")
    assert row["investor_wealth"] == Decimal("109682.20")
    assert row["gross_multiple"] > Decimal("1.6")
