"""Observed marks and cash yields create economic P&L, never synthetic tax alpha.

Monthly borrow, loan interest and manager fees use opening notionals/equity.
Cash costs first consume free cash and then increase the financing loan.
Short dividend substitutes are economic costs; deductibility is not inferred.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.long_short_book import charge, deposit, equity


def apply(book, case, long_return, short_return, long_yield, short_yield):
    costs = dict(
        borrow_cost=money(book["short"] * case.annual_borrow_rate / 12),
        financing_cost=money(book["loan"] * case.annual_financing_rate / 12),
        manager_fee=money(max(Decimal(0), equity(book)) * case.annual_manager_fee / 12),
        short_dividend_cost=money(book["short"] * Decimal(str(short_yield))),
    )
    long_pnl = money(book["long"] * Decimal(str(long_return)))
    short_pnl = -money(book["short"] * Decimal(str(short_return)))
    received = money(book["long"] * Decimal(str(long_yield)))
    book["long"] += long_pnl
    book["short"] -= short_pnl
    deposit(book, received)
    charge(book, sum(costs.values()))
    return dict(
        long_price_pnl=long_pnl, short_price_pnl=short_pnl, long_cash_yield=received, **costs
    )
