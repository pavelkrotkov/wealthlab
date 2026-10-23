"""Explicit opening/closing dates and long-only USD holdings for a trade ledger."""

from datetime import date

from pydantic import Field

from wealthlab.portfolio.models import Lot, Price, Security, TradingAccount
from wealthlab.portfolio.orders import Trade
from wealthlab.tax.facts import TaxModel


class LotCase(TaxModel):
    federal_wash_tracking: bool = False
    opening_wash_context_complete: bool = False
    as_of: date
    end: date
    accounts: list[TradingAccount] = Field(min_length=1)
    securities: list[Security] = Field(min_length=1)
    lots: list[Lot]
    trades: list[Trade]
    closing_prices: dict[str, Price]
