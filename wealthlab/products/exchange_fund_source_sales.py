"""Dated retained-source sales consume actual shares, bases and proceeds in one ordinary trade."""

from wealthlab.portfolio.orders import Trade
from wealthlab.products.exchange_fund_lots import ZERO
from wealthlab.products.exchange_fund_positions import sources
from wealthlab.products.exchange_fund_trades import recognized


def sell_source(ledger, request, observation, row):
    lots = sources(ledger.book, ledger.plan)
    if not lots:
        row["empty_source_sale_requests"] += 1
        return []
    if observation.locked or any(lot.liquid_after > request.date for lot in lots):
        row["denied_source_sales"] += 1
        return []
    quantity = sum((lot.quantity for lot in lots), ZERO)
    trade = Trade(
        id=request.id,
        provenance=request.provenance,
        date=request.date,
        action="sell",
        account_id=ledger.plan.account_id,
        security_id=ledger.plan.source_security.id,
        quantity=quantity,
        price=observation.prices[ledger.plan.source_security.id],
        commission=0,
        selection="specific",
        lot_ids=[lot.id for lot in lots],
    )
    first = len(ledger.book.disposals)
    before = ledger.book.cash[ledger.plan.account_id]
    ledger.book.trade(trade)
    row["source_sale_cash"] += ledger.book.cash[ledger.plan.account_id] - before
    row["source_quantity_sold"] += quantity
    return [
        recognized(
            ledger.book,
            ledger.plan,
            first,
            request.date,
            "Actual retained source sale; cash applied once",
        )
    ]
