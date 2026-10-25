"""Execute actual strike trades through the tested share/cash/two-basis book.

Tax premium adjustments do not create another cash payment. Rejected broker
trades preserve owned shares and pending delivery rather than erasing exposure.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.orders import Trade
from wealthlab.products.option_basis import adjust_basis
from wealthlab.products.option_math import units


def shares(state):
    return sum((lot.quantity for lot in state.book.lots.values()), Decimal(0))


def trade_stock(state, leg, mark):
    buy = (leg.kind == "call") == (leg.side == "long")
    amount = money(units(leg) * leg.strike)
    if not buy and shares(state) < units(leg):
        state.failures.append(f"{leg.id}: insufficient shares for physical delivery")
        return False
    if buy and not state.fund(amount + leg.closing_fee):
        state.failures.append(f"{leg.id}: unfunded physical purchase")
        return False
    trade = Trade(
        id=f"exercise_{leg.id}",
        provenance="assumption",
        date=mark.date,
        action="buy" if buy else "sell",
        account_id=state.account,
        security_id="STOCK",
        quantity=units(leg),
        price=leg.strike,
        commission=leg.closing_fee,
    )
    first = len(state.book.disposals)
    if not execute(state, trade):
        return False
    adjust_basis(state, leg, buy, trade.id, first)
    return True


def unwind_stock(state, mark):
    quantity = shares(state)
    if not quantity:
        return True
    return execute(
        state,
        Trade(
            id="complete_unwind",
            provenance="assumption",
            date=mark.date,
            action="sell",
            account_id=state.account,
            security_id="STOCK",
            quantity=quantity,
            price=mark.stock,
            commission=state.case.stock_sale_fee,
        ),
    )


def execute(state, trade):
    """Keep unpaid option debt outside the long-only Book during actual trades.

    Book fee settlement assumes nonnegative cash. Temporarily isolating an unpaid
    option settlement lets sale proceeds reduce it without inventing a fee debt.
    Rejected delivery/exit trades retain holdings and the original obligation.
    """
    payable = min(state.book.cash[state.account], Decimal(0))
    state.book.cash[state.account] -= payable
    try:
        state.book.trade(trade)
    except ValueError as error:
        state.failures.append(f"{trade.id}: {error}")
        return False
    finally:
        state.book.cash[state.account] += payable
    return True
