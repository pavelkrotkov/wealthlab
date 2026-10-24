"""Flat one-month paths and explicit fees permit independent balance-sheet checks."""

from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.products.long_short_example import synthetic
from wealthlab.products.long_short_inputs import LongShortCase


def flat(**updates):
    data = synthetic()
    terms = dict(
        data["sleeve"],
        annual_borrow_rate=0,
        annual_financing_rate=0,
        annual_manager_fee=0,
        turnover_cost=0,
        exit_cost=0,
        rebalance="none",
    )
    terms.update(updates)
    market = data["market"]
    market.update(end="2026-02-01", expected_annual_inflation=0)
    for asset in market["assets"]:
        asset.update(expected_annual_mark_return=0, annual_cash_yield=0)
    return LongShortCase.model_validate(terms), MarketCase.model_validate(market)


def batch(case):
    return generate(case)
