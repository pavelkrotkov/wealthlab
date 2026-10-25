"""Broker collateral is a supplied contractual scenario, never a universal margin formula."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.option_math import units
from wealthlab.products.option_stock import shares
from wealthlab.products.option_valuation import value


def margin(self, mark):
    available_shares = shares(self) if self.case.cover_stock_calls else Decimal(0)
    required = Decimal(0)
    for leg in self.active.values():
        if leg.side != "short":
            continue
        quantity = units(leg)
        if leg.underlying == "STOCK" and leg.kind == "call":
            covered = min(available_shares, quantity)
            available_shares -= covered
            quantity -= covered
        base = getattr(mark, leg.underlying.lower()) * self.case.short_collateral_fraction
        if leg.kind == "put" and self.case.cash_secure_puts:
            base = leg.strike
        required += quantity * (base + value(leg, mark))
    self.collateral = money(required)
    self.fund(self.collateral)
    return max(Decimal(0), self.collateral - self.book.cash[self.account])
