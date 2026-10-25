"""Actual inventory and restrictions, independent of NAV or acceptance metadata.

An inactive fund can coexist with retained source or distributed basket shares.
Actual lot locks also restrict retained-only capital even when no fund was opened.
"""

from wealthlab.household.calendar import money
from wealthlab.products.exchange_fund_lots import ZERO


def sources(book, plan):
    # Wash allocation may split an original lot into new IDs; security identity survives.
    return [lot for lot in book.lots.values() if lot.security_id == plan.source_security.id]


def snapshot(ledger, observation):
    source = sources(ledger.book, ledger.plan)
    return dict(
        retained_source_quantity=sum((lot.quantity for lot in source), ZERO),
        retained_source_federal_basis=sum((lot.federal_basis for lot in source), ZERO),
        retained_source_nj_basis=sum((lot.nj_basis for lot in source), ZERO),
        remaining_basket_lots=len(ledger.book.lots) - len(source),
        locked_value=locked_value(ledger, observation),
        positions_closed=not ledger.active and not ledger.book.lots,
    )


def locked_value(ledger, observation):
    restricted = sum(
        (
            money(lot.quantity * observation.prices[lot.security_id])
            for lot in ledger.book.lots.values()
            if observation.locked or lot.liquid_after > observation.date
        ),
        ZERO,
    )
    return restricted + (ledger.nav if ledger.active else ZERO)


def exit_status(ledger):
    positions_closed = not ledger.active and not ledger.book.lots
    pending_wash = any(
        row.get("federal_pending_loss", ZERO) or row.get("nj_pending_loss", ZERO)
        for row in ledger.book.disposals
    )
    return dict(
        positions_closed=positions_closed,
        fund_entered=ledger.is_exchange,
        fund_active=ledger.active,
        remaining_source_quantity=sum(
            (lot.quantity for lot in sources(ledger.book, ledger.plan)), ZERO
        ),
        remaining_lots=len(ledger.book.lots),
        unrecognized_future_events=len(ledger.pending),
        pending_wash=pending_wash,
        modeled_exit_complete=positions_closed and not ledger.pending and not pending_wash,
        conditional=True,
        full_tax_optimization_supported=False,
    )
