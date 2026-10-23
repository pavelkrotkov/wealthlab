"""Explicit recurring assessment dates and bases, independent of household fee assumptions."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Money, Record
from wealthlab.portfolio.models import Price
from wealthlab.tax.facts import TaxModel


class FeePeriod(TaxModel):
    start: date
    date: date
    prices: dict[str, Price]
    supplied_base: Money | None = None

    @model_validator(mode="after")
    def period(self) -> Self:
        if self.date < self.start:
            raise ValueError("A fee assessment cannot precede its accrual period.")
        return self


class FeeSchedule(Record):
    kind: Literal["advisor", "manager", "custody", "other"]
    account_ids: list[str] = Field(min_length=1)
    security_ids: list[str] = Field(default_factory=list)
    include_cash: bool = False
    annual_rate: Annotated[Decimal, Field(ge=0, le=1)] = Decimal(0)
    fixed_per_period: Money = Decimal(0)
    day_count: Literal[365, 366, 360] = 365
    payment_account: str
    treatment: Literal["cash", "embedded_in_prices"] = "cash"
    periods: list[FeePeriod] = Field(min_length=1)
