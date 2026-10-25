"""Real trades reuse lot selection, basis recognition, wash matching and rounding."""

from decimal import ROUND_DOWN, Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.generated_orders import identity
from wealthlab.portfolio.orders import Trade
from wealthlab.portfolio.rebalance_state import ZERO, liquid_units

UNIT = Decimal("0.000001")
CENT = Decimal("0.01")


def order(book, policy, security, action, quantity, price):
    book.trade(
        Trade(
            id=identity(book, policy.id, f"{action}_{security}"),
            provenance=policy.provenance,
            date=policy.date,
            action=action,
            account_id=policy.account_id,
            security_id=security,
            quantity=quantity,
            price=price,
            commission=policy.commission_per_trade,
            selection=policy.selection if action == "sell" else "fifo",
        )
    )


def sell(book, policy, security, price, amount):
    quantity = min(
        (amount / price).quantize(UNIT, rounding=ROUND_DOWN), liquid_units(book, policy, security)
    )
    gross = money(quantity * price)
    if quantity <= 0 or gross <= policy.commission_per_trade:
        return ZERO
    order(book, policy, security, "sell", quantity, price)
    return quantity * price


def buy(book, policy, security, price, budget):
    # Whole-cent budgets make nearest-cent trade accounting unable to overdraw.
    gross_budget = budget.quantize(CENT, rounding=ROUND_DOWN)
    quantity = (gross_budget / price).quantize(UNIT, rounding=ROUND_DOWN)
    if quantity > 0 and money(quantity * price) > 0:
        order(book, policy, security, "buy", quantity, price)
