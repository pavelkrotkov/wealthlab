"""Marked net wealth includes each asset, reserve and liability exactly once."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.option_margin import margin
from wealthlab.products.option_math import direction, units
from wealthlab.products.option_stock import shares
from wealthlab.products.option_valuation import value


def snapshot(self, mark):
    option_value = sum(
        (money(direction(leg) * units(leg) * value(leg, mark)) for leg in self.active.values()),
        Decimal(0),
    )
    stock = money(shares(self) * mark.stock)
    shortfall = margin(self, mark)
    cash = self.book.cash[self.account]
    receivable = money(sum(self.entitlements.values(), Decimal(0)))
    row = dict(
        date=mark.date.isoformat(),
        shares=shares(self),
        stock_value=stock,
        option_value=option_value,
        cash=cash,
        outside_cash=self.reserve,
        loan=self.loan,
        collateral=self.collateral,
        available_cash=max(Decimal(0), cash - self.collateral),
        collateral_shortfall=shortfall,
        dividend_receivable=receivable,
        wealth=stock + option_value + cash + self.reserve + receivable - self.loan,
        federal_basis=sum((lot.federal_basis for lot in self.book.lots.values()), Decimal(0)),
        nj_basis=sum((lot.nj_basis for lot in self.book.lots.values()), Decimal(0)),
    )
    self.rows.append(row)
    return row
