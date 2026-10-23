"""Decision information and missing annual forecasts must not manufacture a tax benefit."""

from test_harvest_comparison import harvest_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_closing_prices_change_outcomes_but_not_prior_harvest_orders():
    payload = harvest_case()
    original = run(LotCase.model_validate(payload))
    payload["closing_prices"] = {"STOCK": "200", "ETF": "1"}
    shocked = run(LotCase.model_validate(payload))
    assert shocked["executed_trades"] == original["executed_trades"]
    assert shocked["gross_wealth"] != original["gross_wealth"]


def test_missing_tax_forecasts_remain_unknown_in_both_comparisons():
    payload = harvest_case()
    payload["lot_tax_cases"] = []
    result = run(LotCase.model_validate(payload))["harvest_comparison"]
    for view in ("holding", "terminal_exit"):
        assert result[view]["total_tax_saving"] is None
        assert result[view]["tax_adjusted_difference"] is None
        assert result[view]["gross_wealth_difference"] == 0


def test_harvest_reconsiders_lots_split_by_same_day_wash_matching():
    """The older 50-share sale splits a recent 100-share purchase into two lots.

    Both pieces must remain eligible for this liquidation/replace decision.
    The recovered deferred loss is recognized when the replacement piece sells.
    """
    payload = harvest_case()
    payload["lots"][0].update(quantity="50", federal_basis="500", nj_basis="500")
    payload["trades"] = [
        dict(
            id="recent",
            provenance="assumption",
            date="2026-05-20",
            action="buy",
            account_id="brokerage",
            security_id="STOCK",
            quantity="100",
            price="10",
            commission="0",
        )
    ]
    payload["harvest_policies"][0]["selection"] = "fifo"
    result = run(LotCase.model_validate(payload))
    assert sum(row["sold_units"] for row in result["harvest_decisions"]) == 150
    assert all(lot["security_id"] == "ETF" for lot in result["lots"])
    assert result["harvest_loss_summary"]["federal_recognized_gain"] == -375
