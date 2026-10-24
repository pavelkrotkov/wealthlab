"""Separate short-sale collateral, borrowings and free cash; proceeds are not income.

Opening long purchases use investor capital first, then a full-recourse loan.
Short proceeds remain segregated, earn no interest and cannot finance longs.
A positive net asset value does not make locked positions redeemable.
"""

from decimal import Decimal

from wealthlab.household.calendar import money

ZERO = Decimal(0)


def opening(case):
    book = dict(
        long=money(case.opening_equity * case.long_multiple),
        short=money(case.opening_equity * case.short_multiple),
        collateral=money(case.opening_equity * case.short_multiple),
        cash=ZERO,
        loan=ZERO,
        outside=case.outside_cash,
        closed=False,
    )
    balance(book, case.opening_equity)
    charge(book, money(gross(book) * case.turnover_cost))
    return book


def equity(book):
    return book["long"] + book["cash"] + book["collateral"] - book["short"] - book["loan"]


def gross(book):
    return book["long"] + book["short"]


def charge(book, amount):
    cash = min(book["cash"], amount)
    book["cash"] -= cash
    book["loan"] += amount - cash


def deposit(book, amount):
    repayment = min(book["loan"], amount)
    book["loan"] -= repayment
    book["cash"] += amount - repayment


def balance(book, value):
    # Reconcile free cash/loan after trading; segregated collateral stays separate.
    free = value - book["long"] - book["collateral"] + book["short"]
    book.update(cash=max(ZERO, free), loan=max(ZERO, -free))


def snapshot(book):
    value = equity(book)
    return dict(
        long_value=book["long"],
        short_liability=book["short"],
        short_collateral=book["collateral"],
        free_cash=book["cash"],
        financing_loan=book["loan"],
        equity=value,
        outside_cash=book["outside"],
        investor_wealth=value + book["outside"],
        gross_exposure=gross(book),
        net_exposure=book["long"] - book["short"],
        gross_multiple=gross(book) / value if value > 0 else None,
        closed=book["closed"],
        insolvency=max(ZERO, -value),
    )
