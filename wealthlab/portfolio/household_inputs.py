"""Linked taxable lots have one value, one cash sweep and explicit sale permission."""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Money
from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.models import Price
from wealthlab.tax.facts import TaxModel


class HouseholdMarks(TaxModel):
    date: date
    prices: dict[str, Price]


class LotFundingSource(TaxModel):
    account_id: str
    security_id: str
    selection: Literal["fifo", "hifo"]
    commission: Money


class HouseholdLots(TaxModel):
    case: LotCase
    opening_prices: dict[str, Price]
    monthly_marks: list[HouseholdMarks] = Field(min_length=1)
    funding_sources: list[LotFundingSource] = Field(default_factory=list)
    complete_ownership_and_outside_purchases_confirmed: bool
    monthly_settlement_and_cash_sweep_confirmed: bool
    funding_priority: Literal["linked_lots_before_other_permitted_accounts"]
