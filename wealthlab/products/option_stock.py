"""Actual strike trades reuse the existing share selection, cash and two-basis lot engine."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.orders import Trade
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
    state.book.trade(trade)
    adjust_basis(state, leg, buy, trade.id, first)
    return True


def unwind_stock(state, mark):
    quantity = shares(state)
    if not quantity:
        return True
    try:
        state.book.trade(
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
            )
        )
    except ValueError as error:
        state.failures.append(f"complete_unwind: {error}")
        return False
    return True


def adjust_basis(state, leg, buy, trade_id, first):
    from wealthlab.products.option_basis import adjust_basis as adjust

    adjust(state, leg, buy, trade_id, first)
