"""Rejected purchases do not move reserve cash; collateral still funds available amounts."""

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


@pytest.mark.parametrize(
    "physical,cash,reserve,reason",
    [(False, "0", "200", "opening premium"), (True, "500", "5000", "physical purchase")],
)
def test_unfunded_transaction_preserves_unspent_external_reserve(physical, cash, reserve, reason):
    data = one_leg(physical=physical)
    data["holdings"]["accounts"][0]["cash"] = cash
    data["outside_cash"] = reserve
    result = run(parse(data))
    assert result["ending"]["cash"] == 0
    assert result["ending"]["outside_cash"] == int(reserve)
    assert result["ending"]["shares"] == 100
    assert any(reason in message for message in result["failures"])


def test_margin_still_transfers_partial_reserve_and_reports_remaining_requirement():
    data = one_leg(side="short")
    data["holdings"]["accounts"][0]["cash"] = "0"
    data.update(outside_cash="200", cover_stock_calls=False)
    opening = run(parse(data))["rows"][0]
    assert opening["cash"] == 700
    assert opening["outside_cash"] == 0
    assert opening["collateral_shortfall"] > 0
