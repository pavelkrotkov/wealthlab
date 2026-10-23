"""Allocate basis and net proceeds exactly across partially disposed lots."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.lot_parts import split
from wealthlab.portfolio.models import Lot


def is_long(start, sold) -> bool:
    # More than one calendar year, including the leap-day boundary. A federal
    # holding start can precede acquisition when a prior holding period is tacked.
    return (sold.year, sold.month, sold.day) > (start.year + 1, start.month, start.day)


def dispose(lot, quantity, proceeds, trade) -> tuple[Lot, dict]:
    taken, remaining = split(lot, quantity)
    federal_basis, nj_basis, economic = taken.federal_basis, taken.nj_basis, taken.economic_basis
    result = dict(
        trade_id=trade.id,
        lot_id=lot.id,
        account_id=lot.account_id,
        security_id=lot.security_id,
        date=trade.date.isoformat(),
        quantity=quantity,
        federal_holding_start=lot.federal_holding_start.isoformat(),
        proceeds=proceeds,
        federal_basis=federal_basis,
        nj_basis=nj_basis,
        federal_gross_gain=proceeds - federal_basis,
        nj_gross_gain=proceeds - nj_basis,
        economic_pnl=proceeds - economic if economic is not None else None,
        federal_character="long_term"
        if is_long(lot.federal_holding_start, trade.date)
        else "short_term",
    )
    return remaining, result


def split_proceeds(portions, trade, proceeds):
    remaining = proceeds
    for index, (lot, quantity) in enumerate(portions):
        allocated = money(proceeds * quantity / trade.quantity)
        if index == len(portions) - 1:
            allocated = remaining
        remaining -= allocated
        yield lot, quantity, allocated
    assert remaining == Decimal(0)
