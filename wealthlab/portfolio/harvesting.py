"""Execute loss/replacement pairs through the existing cash and jurisdiction ledgers."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio import harvest_selection
from wealthlab.portfolio.harvest_orders import pair


def execute(book, policy):
    records = []
    if harvest_selection.replacement_blocked(book, policy):
        return [dict(policy=policy.id, status="replacement blocked by recent household loss sale")]
    remaining = policy.max_gross_sales
    seen = set()
    while (lot := harvest_selection.next_lot(book, policy, seen)) is not None:
        seen.add(lot.id)
        quantity = harvest_selection.quantity(lot, policy, remaining)
        if not quantity:
            continue
        orders = pair(book, policy, lot, quantity, len(seen))
        if orders is None:
            continue
        sale, purchase = orders
        book.trade(sale)
        book.trade(purchase)
        book.harvest_sales.add(sale.id)
        gross = money(quantity * sale.price)
        remaining = None if remaining is None else remaining - gross
        records.append(
            dict(
                policy=policy.id,
                date=policy.date.isoformat(),
                status="harvested",
                sale_id=sale.id,
                replacement_id=purchase.id,
                source_lot=lot.id,
                sold_units=quantity,
                replacement_units=purchase.quantity,
                gross_proceeds=gross,
                transaction_costs=2 * sale.commission,
            )
        )
    return records or [
        dict(
            policy=policy.id,
            status="no eligible liquid loss exceeds thresholds",
            sold_units=Decimal(0),
        )
    ]
