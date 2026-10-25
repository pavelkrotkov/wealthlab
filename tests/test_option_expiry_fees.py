"""Lapse and executable termination charges are distinct supplied broker terms."""

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_worthless_physical_lapse_does_not_invent_a_close_or_delivery_commission():
    data = one_leg(physical=True)
    data["marks"][-1]["stock"] = "80"
    data["legs"][0].update(closing_fee="25", expiry_fee="0")
    result = run(parse(data))
    assert result["ending"]["cash"] == 9500
    assert result["terminations"][0]["pnl"] == -500
    assert result["terminations"][0]["termination_fee"] == 0


def test_explicit_lapse_fee_reduces_cash_and_recognized_pnl_once():
    data = one_leg(physical=True)
    data["marks"][-1]["stock"] = "80"
    data["legs"][0].update(closing_fee="25", expiry_fee="3")
    result = run(parse(data))
    assert result["ending"]["cash"] == 9497
    assert result["terminations"][0]["pnl"] == -503
