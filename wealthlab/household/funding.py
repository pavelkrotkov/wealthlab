"""Spend only available cash, preserving balances and reporting unmet obligations."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.household.scenario import Scenario


class Wallet:
    def __init__(self, scenario: Scenario):
        self.cash_ids = [account.id for account in scenario.accounts if account.wrapper == "cash"]
        self.balances = {
            account.id: money(
                account.balance * Decimal(str(scenario.usd_per_currency[account.currency]))
            )
            for account in scenario.accounts
        }

    @property
    def cash(self) -> Decimal:
        return sum((self.balances[key] for key in self.cash_ids), Decimal(0))

    def deposit(self, value: Decimal) -> None:
        self.balances[self.cash_ids[0]] += value

    def pay(self, requested: Decimal) -> Decimal:
        remaining = requested
        for key in self.cash_ids:
            paid = min(self.balances[key], remaining)
            self.balances[key] -= paid
            remaining -= paid
        return requested - remaining
