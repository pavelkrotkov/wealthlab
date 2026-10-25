"""Optional month-end investment budgets buy actual shares with available cash."""

from datetime import date

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.portfolio.rebalance_inputs import Fraction


class SavingPolicy(Record):
    date: date
    account_id: Identifier
    amount: Money
    target_weights: dict[Identifier, Fraction] = Field(min_length=1)
    commission_per_trade: Money
    minimum_cash: Money
