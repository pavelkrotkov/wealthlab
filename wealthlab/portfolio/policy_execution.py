"""Execute policies through the same cash, selection and wash ledger as explicit trades."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.concentration import ratio
from wealthlab.portfolio.policy_amounts import eligible_lots, positions, requested
from wealthlab.portfolio.policy_order import sale
from wealthlab.portfolio.tax_budget import choose, diagnostics


def execute(case, book, policy):
    before, wealth = positions(book, policy)
    lots = eligible_lots(case, book, policy)
    desired = (
        choose(case, book, policy, lots)
        if policy.mode == "tax_budget"
        else requested(case, book, policy)
    )
    available = sum((lot.quantity for lot in lots), Decimal(0))
    quantity = min(desired, available)
    price = policy.prices[policy.security_id]
    if money(quantity * price) < policy.commission:
        quantity = Decimal(0)
    if quantity:
        book.trade(sale(policy, quantity, lots))
    after, closing_wealth = positions(book, policy)
    result = dict(
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
    if policy.mode == "tax_budget":
        result.update(diagnostics(case, book, policy))
    return result
