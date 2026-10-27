"""Spend only available cash, preserving balances and reporting unmet obligations.

A temporary reservation changes availability, never account balances. Required
funding suspends it while comparing gross cash with the complete bill quote;
optional deposits see the reservation until their generator safely finishes.
Closing cash and wealth are observed after the reservation has been released.
"""

from contextlib import contextmanager
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.household.scenario import Scenario


class Wallet:
    def __init__(self, scenario: Scenario):
        self.reserved_cash = Decimal(0)
        self.cash_ids = [account.id for account in scenario.accounts if account.wrapper == "cash"]
        self.balances = {
            account.id: money(
                account.balance * Decimal(str(scenario.usd_per_currency[account.currency]))
            )
            for account in scenario.accounts
        }

    @property
    def cash(self) -> Decimal:
        return max(
            Decimal(0),
            sum((self.balances[key] for key in self.cash_ids), Decimal(0)) - self.reserved_cash,
        )

    @contextmanager
    def reserving(self, amount):
        """Temporarily encumber existing cash without moving it or creating an account."""
        if amount < 0:
            raise ValueError("A wallet reservation cannot be negative.")
        previous = self.reserved_cash
        self.reserved_cash = amount
        try:
            yield
        finally:
            self.reserved_cash = previous

    def deposit(self, value: Decimal) -> None:
        self.balances[self.cash_ids[0]] += value

    def pay(self, requested: Decimal) -> Decimal:
        budget = min(requested, self.cash)
        remaining = budget
        for key in self.cash_ids:
            paid = min(self.balances[key], remaining)
            self.balances[key] -= paid
            remaining -= paid
        return budget - remaining


def opening_wealth(scenario):
    assets = sum(
        a.balance * Decimal(str(scenario.usd_per_currency[a.currency])) for a in scenario.accounts
    )
    debt = sum(
        d.balance * Decimal(str(scenario.usd_per_currency[d.currency])) for d in scenario.debts
    )
    return assets - debt
