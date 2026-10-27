"""Actual benchmark share funding uses observed prices and the ordinary trade/wash ledger."""

from decimal import ROUND_DOWN, ROUND_UP, Decimal

from wealthlab.portfolio.orders import Trade

ZERO = Decimal(0)
SECURITY = "drilling_reference_security"


def fund(ledger, observation, wallet):
    plan, book = ledger.plan, ledger.reference_book
    requested = ledger.call_owed + observation.capital_call
    funded = wallet.pay(requested)
    ledger.call_owed = requested - funded
    book.cash[plan.account_id] += funded
    quantity = (book.cash[plan.account_id] / observation.reference_price).quantize(
        Decimal(".000001"), rounding=ROUND_DOWN
    )
    if funded and not quantity:
        raise ValueError("Reference funding is too small for the supported share precision.")
    if quantity:
        book.trade(order(plan, observation, "buy", quantity))
    return funded


def sell(ledger, observation, requested):
    book = ledger.reference_book
    if observation.reference_locked:
        return
    total = sum((lot.quantity for lot in book.lots.values()), ZERO)
    quantity = (
        total
        if ledger.reference_exit_pending
        else min(
            total,
            (requested / (observation.reference_price)).quantize(
                Decimal(".000001"), rounding=ROUND_UP
            ),
        )
    )
    if quantity:
        book.trade(order(ledger.plan, observation, "sell", quantity))


def order(plan, observation, action, quantity):
    return Trade(
        id=f"drilling_reference_{action}_{observation.id}",
        provenance="assumption",
        date=observation.date,
        action=action,
        account_id=plan.account_id,
        security_id=SECURITY,
        quantity=quantity,
        price=observation.reference_price,
        commission=0,
    )
