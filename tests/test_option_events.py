"""Actual dated exercise, dividends, funding and separately priced rolls.

Dividend entitlement observes the owned shares before exercise trades.
A failed strike payment leaves the delivery obligation outstanding.
"""

from decimal import Decimal

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_supplied_american_assignment_sells_shares_before_later_dividend_entitlement():
    data = one_leg(side="short", physical=True)
    data["legs"][0]["style"] = "american"
    data["events"] = [dict(leg_id="contract", date="2025-06-01", action="exercise")]
    data["dividends"] = [dict(ex_date="2025-12-31", pay_date="2026-01-01", per_share="2")]
    result = run(parse(data))
    assert result["ending"]["shares"] == 0
    assert result["ending"]["cash"] == 20500


def test_unpaid_dividend_is_a_receivable_until_actual_payment():
    data = one_leg()
    data["dividends"] = [dict(ex_date="2025-06-01", pay_date="2026-01-01", per_share="2")]
    result = run(parse(data))
    assert result["rows"][1]["dividend_receivable"] == 200
    assert result["ending"]["dividend_receivable"] == 0
    assert result["ending"]["cash"] == 11700


def test_unfunded_physical_delivery_remains_an_open_obligation_at_expiry():
    data = one_leg(physical=True, unwind=True)
    data["holdings"]["accounts"][0]["cash"] = "500"
    data.update(outside_cash="0", allow_settlement_loan=False)
    result = run(parse(data))
    assert result["open_legs"] == ["contract"]
    assert result["ending"]["phase"] == "unwind_incomplete"
    assert "unfunded physical purchase" in result["failures"][0]


def test_roll_closes_old_leg_at_supplied_quote_and_pays_new_premium_once():
    """The old gain and new cost both survive; rolling does not reset economic history."""
    data = one_leg()
    original = data["legs"][0]
    original["rolls_to"] = "rolled"
    data["legs"].append(
        dict(original, id="rolled", rolls_to=None, opened="2025-06-01", premium="7")
    )
    data["events"] = [dict(leg_id="contract", date="2025-06-01", action="close", close_price="6")]
    result = run(parse(data))
    assert sum(row["pnl"] for row in result["terminations"]) == Decimal(1400)
    assert result["ending"]["cash"] == 11400
