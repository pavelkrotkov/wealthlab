"""Reserve current bills/tax and the chosen cash buffer before optional share purchases.

Quotes use the current recognized return and actual payroll/source withholding.
A purchase can change wash recognition; the ordinary final tax-funding pass still
runs afterward, using that updated return and only explicitly permitted assets.
"""

from decimal import Decimal

from wealthlab.portfolio.household_book import sweep, sync
from wealthlab.portfolio.rebalance_orders import buy
from wealthlab.tax.funding_tax import due

ZERO = Decimal(0)


def available(tax, wallet, start, end, minimum_cash):
    context = tax.funding_context
    if not context["active"] or context["period"] != (start, end):
        raise ValueError("Saving requires the active household tax month.")
    required = context["required"]
    bills = required() if callable(required) else required
    taxes = due(tax.case, tax, context["amounts"], start, end)
    return max(ZERO, wallet.cash - bills - taxes - minimum_cash)


def execute(lots, tax, policy, wallet, start, end):
    budget = min(policy.amount, available(tax, wallet, start, end, policy.minimum_cash))
    if wallet.pay(budget) != budget:
        raise ValueError("Optional saving cannot borrow household cash.")
    lots.book.cash[policy.account_id] += budget
    first = len(lots.book.history)
    for security, weight in sorted(policy.target_weights.items()):
        amount = budget * weight - policy.commission_per_trade
        if amount > 0 and security not in lots.locked:
            buy(lots.book, policy, security, lots.prices[security], amount)
    trades = lots.book.history[first:]
    returned = sweep(lots.book, wallet)
    sync(lots.book, wallet, lots.prices)
    spent = budget - returned
    return dict(
        id=policy.id,
        date=policy.date.isoformat(),
        account_id=policy.account_id,
        requested=policy.amount,
        spent=spent,
        unfilled=policy.amount - spent,
        commissions=sum((t.commission for t in trades), ZERO),
        returned_cash=returned,
        trades=[t.model_dump(mode="json") for t in trades],
    )
