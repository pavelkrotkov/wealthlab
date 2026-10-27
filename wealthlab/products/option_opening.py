"""Native cash stock purchase and premium execution, before valuation or collateral funding."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.orders import Trade
from wealthlab.products.option_book import OptionBook
from wealthlab.products.option_events import open_leg
from wealthlab.products.option_reporting import snapshot
from wealthlab.products.option_stock import execute
from wealthlab.products.option_tax import yearend
from wealthlab.products.option_timing import dividends, terminations


def open_at_mark(state, mark):
    purchase(state, mark)
    for leg in state.case.legs:
        if leg.opened == mark.date:
            open_leg(state, leg, mark)


def purchase(state, mark):
    order = state.case.opening_stock_purchase
    if order is None or order.date != mark.date:
        return
    cost = money(Decimal(order.shares) * mark.stock) + order.fee
    if not state.fund(cost, require_full=True):
        state.failures.append(f"{order.id}: unfunded opening stock purchase")
        return
    trade = Trade(
        id=order.id,
        provenance=order.provenance,
        date=order.date,
        action="buy",
        account_id=state.account,
        security_id="STOCK",
        quantity=order.shares,
        price=mark.stock,
        commission=order.fee,
    )
    if execute(state, trade):
        # Book.trade already paid the cash and capitalized the commission once.
        state.cash_movements.append(
            dict(date=mark.date.isoformat(), label=f"stock_buy:{order.id}", amount=-cost)
        )


def opening_state(case):
    """A fresh native book supports preflight/stress; it never mutates the supplied plan."""
    state = OptionBook(case)
    mark = case.marks[0]
    # Observe the old holder's ex-date rights before buying, then execute any
    # supplied same-day exercise/close exactly as the actual native engines do.
    dividends(state, mark)
    open_at_mark(state, mark)
    terminations(state, mark, same_day=True)
    yearend(state, mark)
    row = snapshot(state, mark)
    return state, row
