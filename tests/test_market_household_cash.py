"""Separate market cash yield enters cash and federal/NJ recognition only once.

A flat $100k stock position pays $2k per month. Federal standard deductions
cover the ordinary dividends; NJ annual gross $24k less $2k personal exemption
incurs $315 each year. Starting wealth $101k plus $48k cash less $630 tax
therefore ends at $148,370, without any phantom reinvestment or lot basis.
"""

import pytest

from tests.market_household_cases import flat
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


@pytest.fixture(scope="module")
def projection():
    case, market, binding = flat(cash_yield=0.24)
    original = case.model_dump_json()
    result = run(case, generate(market), binding)
    return case, original, result


def test_actual_market_yield_and_tax_conserve_household_capital(projection):
    _, _, result = projection
    rows = result["details"][0]["rows"]
    assert sum(r["market_cash_yield"] for r in rows) == 48000
    assert rows[-1]["net_wealth"] == 148370
    assert rows[11]["annual_tax"]["federal"]["agi"] == 24000
    assert rows[11]["annual_tax"]["new_jersey"]["income_tax"] == 315
    assert rows[-1]["account_balances"]["brokerage"] == 100000


def test_horizon_and_probability_scope_and_source_immutability(projection):
    case, original, result = projection
    assert result["outcomes"][0]["funded"]
    assert case.model_dump_json() == original
    assert result["aggregate"]["monte_carlo_95_wilson"] is None
    assert not result["aggregate"]["horizon_covers_target_age"]
