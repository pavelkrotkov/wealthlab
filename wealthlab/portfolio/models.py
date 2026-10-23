"""Long-only trade inputs with explicit units, ownership and jurisdiction bases."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Money, Record

Quantity = Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=6)]
Price = Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=8)]


class TradingAccount(Record):
    owner: Literal["primary", "spouse", "joint"]
    wrapper: Literal["taxable", "traditional_ira", "roth_ira"]
    cash: Money


class Security(Record):
    wash_group: str = Field(min_length=1, max_length=80)
    kind: Literal["stock", "etf", "bond", "collectible"]
    exposure_group: str = Field(min_length=1, max_length=80)


class Lot(Record):
    account_id: str
    security_id: str
    acquired: date
    federal_holding_start: date
    liquid_after: date
    quantity: Quantity
    federal_basis: Money
    nj_basis: Money

    @model_validator(mode="after")
    def holding_date(self) -> Self:
        if self.federal_holding_start > self.acquired:
            raise ValueError("Federal holding start cannot follow actual acquisition.")
        return self
