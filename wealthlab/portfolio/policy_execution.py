"""Execute policies through the same cash, selection and wash ledger as explicit trades."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.concentration import ratio
from wealthlab.portfolio.orders import Trade
from wealthlab.portfolio.policy_amounts import eligible_lots, positions, requested


def execute(case, book, policy):
    before, wealth = positions(book, policy)
    desired = requested(case, book, policy)
    lots = eligible_lots(case, book, policy)
    available = sum((lot.quantity for lot in lots), Decimal(0))
    quantity = min(desired, available)
    price = policy.prices[policy.security_id]
    if money(quantity * price) < policy.commission:
        quantity = Decimal(0)
    if quantity:
        trade = Trade(
            id=policy.id,
            provenance=policy.provenance,
            date=policy.date,
            action="sell",
            account_id=policy.account_id,
            security_id=policy.security_id,
            quantity=quantity,
            price=price,
            commission=policy.commission,
            selection="specific",
            lot_ids=[lot.id for lot in lots],
        )
        book.trade(trade)
    after, closing_wealth = positions(book, policy)
    return dict(
        policy=policy.id,
        date=policy.date.isoformat(),
        mode=policy.mode,
        requested_units=desired,
        sold_units=quantity,
        unfilled_units=desired - quantity,
        weight_before=ratio(before, wealth),
        weight_after=ratio(after, closing_wealth),
        target_fraction=policy.fraction,
        commission=policy.commission if quantity else Decimal(0),
    )


def replay(case, book):
    """Manual trades precede policies on the same day; each list preserves tie order.

    No closing valuation enters a decision. Later decisions see earlier executions,
    including updated lot basis, but cannot see future orders or price snapshots.
    """
    events = [(trade.date, 0, index, trade) for index, trade in enumerate(case.trades)]
    events += [(item.date, 1, index, item) for index, item in enumerate(case.sale_policies)]
    decisions = []
    for _, kind, _, event in sorted(events, key=lambda item: item[:3]):
        if kind == 0:
            book.trade(event)
        else:
            decisions.append(execute(case, book, event))
    return decisions
