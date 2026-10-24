"""Resolved liquidation and insolvency have different product outcomes."""

from long_short_cases import batch, flat
from test_long_short_margin import squeezed

from wealthlab.markets.inputs import MarketCase
from wealthlab.products.long_short_run import run


def test_forced_liquidation_can_resolve_margin_without_a_product_failure():
    case, market = flat(maintenance_fraction_of_gross="0.6", exit_at_horizon=False)
    data = market.model_dump(mode="json")
    data.update(mode="stress", shocks=[dict(name="squeeze", month=0, mark_shocks=dict(short=1))])
    summary = run(case, batch(MarketCase.model_validate(data)))["details"][0]["summary"]
    assert summary["margin_trigger_months"] == summary["forced_liquidations"] == 1
    assert summary["remaining_loan"] == summary["negative_equity_months"] == 0
    assert not summary["margin_failure"]
    assert summary["product_feasible"]


def test_unpaid_debt_is_not_a_repeated_unresolved_margin_call():
    summary = squeezed(10000)["summary"]
    assert summary["remaining_loan"] == 10000
    assert summary["negative_equity_months"] == 1
    assert not summary["margin_failure"]
    assert not summary["product_feasible"]
