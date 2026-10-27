"""Position identities and actual debt survive a zero marked value or unwind label."""

from decimal import Decimal

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_actual_complete_unwind_reports_cash_without_premium_double_count():
    result = run(parse(one_leg(unwind=True)))
    exit_state = result["exit_state"]
    assert exit_state["modeled_cash_exit_complete"]
    assert exit_state["open_contracts"] == exit_state["stock_lots"] == []
    assert exit_state["cash"] + exit_state["outside_cash"] == 28500
    assert exit_state["borrowed_shares"] == 0
    assert exit_state["external_borrowed_shares"] is None


def test_offsetting_marked_legs_are_not_contractual_exit():
    data = one_leg(unwind=False)
    data["holdings"].update(lots=[])
    data["holdings"]["accounts"][0]["cash"] = "0"
    data.update(outside_cash="0", short_collateral_fraction="0", allow_settlement_loan=False)
    leg = dict(data["legs"][0], premium="0", expiry="2027-01-01")
    data["legs"] = [dict(leg, id="long", side="long"), dict(leg, id="short", side="short")]
    result = run(parse(data))
    exit_state = result["exit_state"]
    assert result["ending"]["option_value"] == result["ending"]["wealth"] == 0
    assert len(exit_state["open_contracts"]) == 2
    assert not exit_state["modeled_positions_closed"]
    assert not exit_state["modeled_cash_exit_complete"]


def test_complete_unwind_label_does_not_discharge_unpaid_cash_settlement():
    # Short call receives500, then pays90,000. No owned stock or cash reserve
    # exists to cap the liability or manufacture the missing89,500.
    data = one_leg(side="short", unwind=True)
    data["holdings"].update(lots=[])
    data["holdings"]["accounts"][0]["cash"] = "0"
    data.update(outside_cash="0", short_collateral_fraction="0", allow_settlement_loan=False)
    data["marks"][-1]["stock"] = "1000"
    result = run(parse(data))
    exit_state = result["exit_state"]
    assert result["ending"]["phase"] == "complete_unwind"
    assert exit_state["modeled_positions_closed"]
    assert exit_state["settlement_cash_payable"] == 89500
    assert not exit_state["modeled_cash_exit_complete"]


def test_borrowed_cash_is_separate_from_borrowed_stock_and_blocks_exit():
    data = one_leg(side="short", unwind=True)
    data["holdings"].update(lots=[])
    data["holdings"]["accounts"][0]["cash"] = "0"
    data.update(
        outside_cash="0",
        short_collateral_fraction="0",
        allow_settlement_loan=True,
        settlement_loan_annual_rate=0,
    )
    data["marks"][-1]["stock"] = "1000"
    exit_state = run(parse(data))["exit_state"]
    assert exit_state["cash"] == 0
    assert exit_state["settlement_loan"] == Decimal(89500)
    assert exit_state["borrowed_shares"] == 0
    assert not exit_state["modeled_cash_exit_complete"]
