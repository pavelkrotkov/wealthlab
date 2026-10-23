"""Explicit opening/closing dates and long-only USD holdings for a trade ledger."""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.portfolio.harvest_policy import HarvestPolicy
from wealthlab.portfolio.models import Lot, Price, Security, TradingAccount
from wealthlab.portfolio.orders import Trade
from wealthlab.portfolio.policies import SalePolicy
from wealthlab.portfolio.terminal_exit import TerminalExit
from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.facts import TaxModel


class LotCase(TaxModel):
    nj_wash_treatment: Literal["unconfirmed", "federal_rules", "no_wash_assumption"] = "unconfirmed"
    federal_wash_tracking: bool = False
    opening_wash_context_complete: bool = False
    lot_tax_cases: list[AnnualCase] = Field(default_factory=list)
    as_of: date
    end: date
    accounts: list[TradingAccount] = Field(min_length=1)
    securities: list[Security] = Field(min_length=1)
    lots: list[Lot]
    trades: list[Trade]
    harvest_policies: list[HarvestPolicy] = Field(default_factory=list)
    compare_harvesting: bool = False
    terminal_exit: TerminalExit | None = None
    sale_policies: list[SalePolicy] = Field(default_factory=list)
    closing_prices: dict[str, Price]
