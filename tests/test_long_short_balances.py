"""Segregated short proceeds are collateral, and full-recourse debt is never clipped away."""

from long_short_cases import batch, flat

from wealthlab.markets.inputs import MarketCase
from wealthlab.products.long_short_book import equity, opening
from wealthlab.products.long_short_run import run


def test_opening_balance_sheet_and_flat_unwind_conserve_investor_capital():
    case, market = flat()
    book = opening(case)
    assert (book["long"], book["short"], book["collateral"], book["loan"]) == (
        130000,
        30000,
        30000,
        30000,
    )
    assert equity(book) == 100000
    last = run(case, batch(market))["details"][0]["rows"][-1]
    assert last["investor_wealth"] == last["outside_cash"] == 110000
    assert last["equity"] == last["financing_loan"] == 0


def test_short_squeeze_can_lose_more_than_initial_investment_and_leave_debt():
    case, market = flat()
    data = market.model_dump(mode="json")
    data.update(mode="stress", shocks=[dict(name="squeeze", month=0, mark_shocks=dict(short=4))])
    result = run(case, batch(MarketCase.model_validate(data)))["details"][0]
    last = result["rows"][-1]
    assert last["short_price_pnl"] == -120000
    assert last["outside_cash"] == 0
    assert last["financing_loan"] == 10000
    assert last["investor_wealth"] == -10000
    assert result["summary"]["forced_liquidations"] == 1
