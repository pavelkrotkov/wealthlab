"""Explicit redemptions and complete unwind conserve value, including full-recourse debt.

A rebalance targets pre-trade observed equity. Actual post-cost leverage is
reported rather than silently assuming transaction costs were free. Partial
redemptions scale both legs and segregated collateral together.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.long_short_book import ZERO, balance, charge, equity, gross


def rebalance(book, case):
    value = equity(book)
    target_long = money(value * case.long_multiple)
    target_short = money(value * case.short_multiple)
    turnover = abs(target_long - book["long"]) + abs(target_short - book["short"])
    book.update(long=target_long, short=target_short, collateral=target_short)
    balance(book, value)
    cost = money(turnover * case.turnover_cost)
    charge(book, cost)
    return dict(turnover_notional=turnover, turnover_cost=cost)


def redeem(book, requested, rate):
    value, exposure = equity(book), gross(book)
    available = value - money(exposure * rate)
    if available <= 0:
        return dict(redemption_paid=ZERO, exit_cost=ZERO)
    fraction = min(Decimal(1), requested / available)
    cost = money(exposure * fraction * rate)
    paid = min(requested, max(ZERO, money(value * fraction) - cost))
    for key in ("long", "short", "collateral"):
        book[key] = money(book[key] * (1 - fraction))
    balance(book, value - cost - paid)
    book["outside"] += paid
    if fraction == 1:
        book["closed"] = True
    return dict(redemption_paid=paid, exit_cost=cost)


def liquidate(book, rate):
    value = equity(book)
    cost = money(gross(book) * rate)
    net = value - cost
    paid = max(ZERO, net)
    debt_paid = min(book["outside"], max(ZERO, -net))
    book.update(long=ZERO, short=ZERO, collateral=ZERO, cash=ZERO, loan=max(ZERO, -net) - debt_paid)
    book["outside"] += paid - debt_paid
    book["closed"] = True
    return dict(liquidation_cash=paid, liquidation_debt_paid=debt_paid, liquidation_cost=cost)
