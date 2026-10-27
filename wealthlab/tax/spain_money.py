"""Translate each dated amount independently; EUR itself has a unit exchange rate."""

from datetime import date
from decimal import Decimal
from typing import Self

from pydantic import Field, model_validator

from wealthlab.household.calendar import money
from wealthlab.tax.facts import SignedMoney, TaxModel


class SpanishAmount(TaxModel):
    amount: SignedMoney
    currency: str = Field(min_length=3, max_length=3)
    date: date
    eur_per_unit: Decimal = Field(gt=0, le=1000000)
    source: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def euro_rate(self) -> Self:
        if self.currency == "EUR" and self.eur_per_unit != 1:
            raise ValueError("EUR amounts require a unit EUR translation rate.")
        return self

    def euros(self):
        return money(self.amount * self.eur_per_unit)


def year_end(value, year):
    if value.date != date(year, 12, 31) or value.amount < 0:
        raise ValueError("Wealth and debt need nonnegative December31 fiscal values and FX.")
