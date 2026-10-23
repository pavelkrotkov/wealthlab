"""Purchases consume account cash and capitalize commissions into both bases."""

from wealthlab.household.calendar import money
from wealthlab.portfolio.models import Lot


def buy(book, trade):
    cost = money(trade.quantity * trade.price) + trade.commission
    lot_id = trade.id
    if lot_id in book.lots:
        raise ValueError("Purchase lot ID collides with an existing lot.")
    if book.cash[trade.account_id] < cost:
        raise ValueError("Purchase exceeds available account cash; borrowing is not assumed.")
    lot = Lot(
        id=lot_id,
        provenance=trade.provenance,
        account_id=trade.account_id,
        security_id=trade.security_id,
        acquired=trade.date,
        federal_holding_start=trade.date,
        liquid_after=trade.date,
        quantity=trade.quantity,
        federal_basis=cost,
        nj_basis=cost,
        economic_basis=cost,
    )
    book.cash[trade.account_id] -= cost
    book.lots[lot.id] = lot
    book.origins[lot.id] = lot.id
