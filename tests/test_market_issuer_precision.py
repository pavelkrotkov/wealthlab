"""Raw issuer marks and rounded cash ledgers must not create concentration above 100%."""

from decimal import Decimal

import pytest

from wealthlab.markets.household_example import synthetic
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


@pytest.mark.parametrize("stress", ["early_crash", "illiquidity"])
def test_single_issuer_stress_never_exceeds_its_total_gross_asset_denominator(stress):
    case, market, binding = synthetic("stress", stress)
    result = run(case, generate(market), binding)
    outcome = result["outcomes"][0]
    assert outcome["issuer_concentration_complete"]
    assert Decimal(0) <= outcome["max_security_weight"] <= 1
    rows = result["details"][0]["rows"]
    for row in rows:
        stock = row["market_security_values"]["stock"]
        cash = row["account_balances"]["cash"]
        expected = stock / (stock + cash) if stock + cash else Decimal(0)
        assert row["market_max_security_weight"] == expected
