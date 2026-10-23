"""Monthly scheduled flows and debt contracts, with explicit effective dates."""

from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Currency, Identifier, Money, Record


class DatedAmount(Record):
    start: date
    end: date
    monthly_amount: Money
    currency: Currency
    annual_growth: float = Field(ge=-0.5, le=1)

    @model_validator(mode="after")
    def dates(self) -> Self:
        if self.end <= self.start:
            raise ValueError("End date is exclusive and must follow start date.")
        return self


class Income(DatedAmount):
    owner: Identifier
    stop_at_retirement: bool


class Expense(DatedAmount):
    category: Literal["essential", "discretionary", "healthcare", "mortgage", "education"]


class Debt(Record):
    currency: Currency
    balance: Money
    annual_rate: float = Field(ge=0, le=1)
    monthly_payment: Money


class Contribution(DatedAmount):
    destination: Identifier
