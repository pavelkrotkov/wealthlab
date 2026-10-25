"""Dated allocation choices have explicit cash, turnover and execution constraints."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record

Fraction = Annotated[Decimal, Field(ge=0, le=1)]


class RebalancePolicy(Record):
    date: date
    account_id: Identifier
    target_weights: dict[Identifier, Fraction] = Field(min_length=1)
    drift_band: Fraction
    max_sale_fraction: Fraction
    selection: Literal["fifo", "hifo"]
    commission_per_trade: Money
    funding: Literal["sale_proceeds_only"]
