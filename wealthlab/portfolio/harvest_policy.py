"""Explicit replacement assumptions for dated, long-only loss harvesting."""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Money, Record
from wealthlab.portfolio.models import Price


class HarvestPolicy(Record):
    date: date
    account_id: str
    security_id: str
    replacement_id: str
    replacement_eligible: bool = False
    prices: dict[str, Price]
    minimum_loss: Money = Decimal(100)
    minimum_loss_fraction: Decimal = Field(default=Decimal("0.05"), ge=0, le=1)
    max_gross_sales: Money | None = None
    commission_per_trade: Money = Decimal(0)
    selection: Literal["fifo", "hifo"] = "hifo"
