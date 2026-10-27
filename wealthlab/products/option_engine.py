"""Dated option cash, marked exposure, actual shares/basis, and complete liquidation."""

from decimal import Decimal

from wealthlab.products.option_book import OptionBook
from wealthlab.products.option_events import finish
from wealthlab.products.option_financing import accrue
from wealthlab.products.option_leg_marks import leg_mark
from wealthlab.products.option_opening import open_at_mark
from wealthlab.products.option_reporting import snapshot
from wealthlab.products.option_result import report
from wealthlab.products.option_stock import unwind_stock
from wealthlab.products.option_tax import yearend
from wealthlab.products.option_timing import dividends, terminations
from wealthlab.products.option_validation import validate


def run(case):
    validate(case)
    state = OptionBook(case)
    leg_rows = []
    previous = case.marks[0].date
    for mark in case.marks:
        accrue(state, previous, mark.date)
        previous = mark.date
        dividends(state, mark)
        terminations(state, mark, same_day=False)
        open_at_mark(state, mark)
        terminations(state, mark, same_day=True)
        leg_rows.extend(leg_mark(leg, mark) for leg in state.active.values())
        yearend(state, mark)
        snapshot(state, mark)
    held = dict(state.rows[-1])
    if case.unwind:
        complete_unwind(state, case.marks[-1])
    return report(state, held, leg_rows)


def complete_unwind(state, mark):
    """Retain actual shares if the broker rejects their sale.

    Repay debt only from cash left after the trades that actually executed.
    A failed stock exit remains an incomplete unwind in the returned report.
    """
    for leg in list(state.active.values()):
        if leg.expiry > mark.date:
            finish(state, leg, mark, "close")
    stock_unwound = unwind_stock(state, mark)
    cash = state.book.cash[state.account]
    repaid = min(max(Decimal(0), cash), state.loan)
    state.loan -= repaid
    state.book.cash[state.account] -= repaid
    row = snapshot(state, mark)
    row["phase"] = "unwind_incomplete" if state.active or not stock_unwound else "complete_unwind"
