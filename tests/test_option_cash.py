"""Cash/basis checks derive directly from strike delivery and actual premium payments."""

from decimal import Decimal

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


@pytest.mark.parametrize(
    "kind,side,spot,pnl",
    [
        ("call", "long", "120", 1500),
        ("call", "short", "120", -1500),
        ("put", "long", "80", 1500),
        ("put", "short", "80", -1500),
        ("call", "long", "80", -500),
    ],
)
def test_cash_expiry_conserves_premium_and_payoff(kind, side, spot, pnl):
    data = one_leg(kind, side)
    data["marks"][-1]["stock"] = spot
    result = run(parse(data))
    assert result["terminations"][0]["pnl"] == pnl
    assert sum(r["amount"] for r in result["cash_movements"]) == pnl
    assert result["ending"]["wealth"] == Decimal(15000) + Decimal(spot) * 100 + pnl


def test_exhausted_cash_settlement_retains_unlimited_liability():
    data = one_leg(side="short")
    data["holdings"]["accounts"][0]["cash"] = "0"
    data.update(outside_cash="0", short_collateral_fraction="0", cover_stock_calls=False)
    data["marks"][-1]["stock"] = "1000"
    result = run(parse(data))
    assert result["ending"]["cash"] == -89500
    assert result["ending"]["wealth"] == 10500
