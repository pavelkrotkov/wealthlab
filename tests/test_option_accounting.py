"""Cash/basis checks derive directly from strike delivery and actual premium payments."""

from decimal import Decimal

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


@pytest.mark.parametrize(
    "kind,side,spot,expected_cash,expected_shares,fed,nj",
    [
        ("call", "long", "120", "9500", "200", "15500", "16500"),
        ("put", "short", "80", "10500", "200", "14500", "15500"),
        ("call", "short", "120", "20500", "0", "0", "0"),
        ("put", "long", "80", "19500", "0", "0", "0"),
    ],
)
def test_physical_delivery_updates_actual_cash_and_two_bases(
    kind, side, spot, expected_cash, expected_shares, fed, nj
):
    data = one_leg(kind, side, physical=True)
    data["marks"][-1]["stock"] = spot
    if expected_shares == "200":
        data["holdings"]["accounts"][0]["cash"] = "20000"
        data["outside_cash"] = "0"
    result = run(parse(data))
    end = result["ending"]
    assert end["cash"] == Decimal(expected_cash)
    assert end["shares"] == Decimal(expected_shares)
    assert end["federal_basis"] == Decimal(fed)
    assert end["nj_basis"] == Decimal(nj)
    assert_delivery_tax(result, end, expected_cash)


def assert_delivery_tax(result, end, expected_cash):
    if end["shares"] == 0:
        assert not [r for r in result["tax"] if r["id"].startswith("contract:")]
        assert result["disposals"][0]["federal_gross_gain"] == Decimal(expected_cash) - 15000
