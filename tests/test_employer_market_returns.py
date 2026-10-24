"""Vested/contingent growth cannot become household cash or inferred tax allocations."""

from decimal import Decimal

import pytest
from employer_market_cases import flat

from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


@pytest.fixture(scope="module")
def projection():
    household, market, binding = flat()
    return household, run(household, generate(market), binding)


def compound(value):
    for _ in range(12):
        value = (value * Decimal("1.02")).quantize(Decimal(".01"))
    return value


def test_growth_stays_in_both_pockets_and_cash_income_is_not_duplicated(projection):
    _, result = projection
    rows = result["details"][0]["rows"]
    last = rows[-1]
    assert last["employer_vested"] == compound(Decimal(20000))
    assert last["employer_unvested_contingent"] == compound(Decimal(80000))
    assert sum(r["income"] for r in rows) == 120000
    assert sum(r["market_cash_yield"] for r in rows) == 0
    assert sum(r["tax_event_cash"] for r in rows) == 0
    assert last["annual_tax"]["federal"]["agi"] == 140000
