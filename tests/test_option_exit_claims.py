"""Pending entitlement and future contracts are read without funding or erasing them."""

from datetime import date
from decimal import Decimal

from tests.option_cases import one_leg, parse
from wealthlab.household.projection import project
from wealthlab.products.option_book import OptionBook
from wealthlab.products.option_events import finish, open_leg
from wealthlab.products.option_exit_state import evidence, from_rows
from wealthlab.products.option_household_example import synthetic
from wealthlab.products.option_inputs import OptionDividend
from wealthlab.products.option_stock import unwind_stock
from wealthlab.products.option_timing import dividends


def test_dividend_entitlement_survives_actual_stock_and_option_close_until_paid():
    # Owning stock on ex-date creates a claim even after actual liquidation.
    # Closing the option returns its supplied premium; stock adds10,000 to the
    # original10,000 inside cash. The later100 dividend must arrive only once.
    case = parse(one_leg())
    first, last = case.marks[0], case.marks[-1]
    dividend = OptionDividend(ex_date=first.date, pay_date=last.date, per_share=Decimal(1))
    state = OptionBook(case.model_copy(update={"dividends": [dividend]}))
    dividends(state, first)
    open_leg(state, case.legs[0], first)
    finish(state, case.legs[0], first, "close", Decimal(5))
    assert unwind_stock(state, first)
    result = evidence(state, first.date)
    assert result["modeled_positions_closed"]
    assert result["dividend_receivable"] == 100
    assert not result["modeled_cash_exit_complete"]
    dividends(state, last)
    assert state.book.cash[state.account] == 20100
    assert evidence(state, last.date)["modeled_cash_exit_complete"]


def test_unopened_future_contract_prevents_early_exit_and_observer_does_not_mutate():
    # Snapshot/margin code can fund collateral; a pure observer must not call it
    # merely to decide whether a scheduled future contract still exists.
    case = parse(one_leg())
    leg = case.legs[0].model_copy(update={"opened": case.holdings.end, "expiry": date(2027, 1, 1)})
    case = case.model_copy(
        update={"legs": [leg], "holdings": case.holdings.model_copy(update={"lots": []})}
    )
    state = OptionBook(case)
    before = (dict(state.book.cash), state.loan, state.reserve, state.collateral)
    result = evidence(state, case.holdings.as_of)
    assert result["unopened_contract_ids"] == [leg.id]
    assert not result["modeled_positions_closed"]
    assert (dict(state.book.cash), state.loan, state.reserve, state.collateral) == before


def test_household_export_observes_post_settle_cash_and_preserves_native_cash_oracle():
    # Gross pre-sweep cash is not residual option cash: household bills already
    # consumed6,000 and the remaining6,500 is in the shared wallet.
    rows = project(synthetic())
    result = from_rows(rows)
    assert rows[-1]["closing_cash"] == rows[-1]["net_wealth"] == 6500
    assert result["cash"] == result["settlement_loan"] == result["collateral"] == 0
    assert result["modeled_cash_exit_complete"]
    assert from_rows([{}]) is None
