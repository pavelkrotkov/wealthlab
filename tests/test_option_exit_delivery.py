"""Native failed delivery/stock sales retain obligations even when one asset count is zero."""

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_missing_stock_does_not_create_borrowed_shares_or_close_assignment():
    data = one_leg(side="short", physical=True, unwind=True)
    data["holdings"]["lots"] = []
    result = run(parse(data))
    state = result["exit_state"]
    assert state["owned_shares"] == state["borrowed_shares"] == 0
    assert len(state["open_contracts"]) == 1
    assert not state["execution_succeeded"]
    assert not state["modeled_cash_exit_complete"]


def test_failed_stock_sale_keeps_the_actual_lot_not_just_a_mark():
    data = one_leg(unwind=True)
    data["marks"][-1]["stock"] = "0.001"
    data["stock_sale_fee"] = "1"
    state = run(parse(data))["exit_state"]
    assert len(state["stock_lots"]) == 1
    assert state["owned_shares"] == 100
    assert not state["modeled_positions_closed"]


def test_failed_opening_is_not_certified_as_an_executed_complete_strategy():
    data = one_leg(unwind=True)
    data["holdings"]["lots"] = []
    data["holdings"]["accounts"][0]["cash"] = "0"
    data.update(outside_cash="0", allow_settlement_loan=False)
    state = run(parse(data))["exit_state"]
    assert state["modeled_positions_closed"]
    assert not state["execution_succeeded"]
    assert not state["modeled_cash_exit_complete"]
