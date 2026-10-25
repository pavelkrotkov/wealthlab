"""Unavailable liquidity, yield conventions and future quote periods fail explicitly."""

import pytest

from tests.option_market_cases import change, flat
from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.option_example import synthetic
from wealthlab.markets.paths import generate


@pytest.mark.parametrize(
    "kind,message",
    [
        ("yield", "zero generated cash yield"),
        ("lock", "liquidity locks"),
        ("total_return", "price-only returns"),
    ],
)
def test_unsupported_market_conventions_do_not_create_historical_option_returns(kind, message):
    scenario, market, binding = synthetic()
    data = market.model_dump(mode="json")
    if kind == "yield":
        data["assets"][0]["annual_cash_yield"] = 0.02
    elif kind == "lock":
        data["mode"] = "stress"
        data["shocks"] = [dict(name="locked delivery", month=0, lock_months=dict(stock=1))]
    else:
        data["return_convention"] = "total_return_reinvested"
    with pytest.raises(ValueError, match=message):
        run(scenario, generate(MarketCase.model_validate(data)), binding)


def test_future_entry_premium_cannot_be_reused_after_generated_prices_change():
    scenario, batch, binding = flat()
    later = change(
        scenario, lambda data: data["option_plan"]["case"]["legs"][0].update(opened="2026-01-31")
    )
    with pytest.raises(ValueError, match="opening contracts only"):
        run(later, batch, binding)


def test_dividends_use_actual_entitlement_and_cash_once_with_ordinary_tax_assumptions():
    scenario, batch, binding = flat("Covered call")

    def setup(data):
        data["option_plan"]["ordinary_dividend_tax_on_cash_receipt_confirmed"] = True
        data["option_plan"]["case"]["dividends"] = [
            dict(ex_date="2026-01-31", pay_date="2026-02-28", per_share="1")
        ]

    result = run(change(scenario, setup), batch, binding)
    final = result["details"][0]["rows"][-1]
    assert final["closing_cash"] == 24700
    assert final["annual_tax"]["federal"]["agi"] == 5700
