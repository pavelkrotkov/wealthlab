"""Select only available shares; HIFO uses federal total basis divided by quantity."""

from decimal import Decimal

from wealthlab.portfolio.models import Lot
from wealthlab.portfolio.orders import Trade


def candidates(lots: dict[str, Lot], trade: Trade) -> list[Lot]:
    """Specific identification honors the user's supplied priority, not HIFO order.

    Stable date/ID tie breaks make repeated runs and strategy comparisons agree.
    The caller still needs to establish that specific identification is available.
    """
    available = [lot for lot in lots.values() if eligible(lot, trade)]
    if trade.selection == "specific":
        selected = {lot.id: lot for lot in available}
        if not set(trade.lot_ids) <= selected.keys():
            raise ValueError("Specific lots must exist, match the account/security and be liquid.")
        return [selected[key] for key in trade.lot_ids]
    if trade.selection == "hifo":
        return sorted(
            available, key=lambda lot: (-lot.federal_basis / lot.quantity, lot.acquired, lot.id)
        )
    return sorted(available, key=lambda lot: (lot.acquired, lot.id))


def select(lots: dict[str, Lot], trade: Trade) -> list[tuple[Lot, Decimal]]:
    available = candidates(lots, trade)
    if sum(lot.quantity for lot in available) < trade.quantity:
        raise ValueError("Sale exceeds the selected liquid shares; no short sale is assumed.")
    remaining = trade.quantity
    portions = []
    for lot in available:
        if remaining == 0:
            break
        quantity = min(remaining, lot.quantity)
        portions.append((lot, quantity))
        remaining -= quantity
    return portions


def eligible(lot: Lot, trade: Trade) -> bool:
    return (
        lot.account_id == trade.account_id
        and lot.security_id == trade.security_id
        and lot.acquired <= trade.date
        and lot.liquid_after <= trade.date
    )
