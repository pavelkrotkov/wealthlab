"""Supplied contract illustrations keep missing values and funding paths explicit."""

from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Money, Record
from wealthlab.products.life_illustration_records import LifeFlow, LifeValue
from wealthlab.tax.facts import TaxModel


class LifeIllustration(Record):
    name: str = Field(min_length=1, max_length=120)
    scale: Literal["guaranteed", "current", "stressed"]
    source: str = Field(min_length=1, max_length=500)
    source_date: date
    issue_date: date
    premium_pattern: Literal["limited_pay", "long_duration", "custom"]
    funding_path: str = Field(min_length=1, max_length=120)
    stop_funding_date: date | None
    complete_history_from_issue_confirmed: bool
    values_match_cashflows_and_funding_path_confirmed: bool
    flows: list[LifeFlow] = Field(default_factory=list)
    values: list[LifeValue] = Field(min_length=1)

    @model_validator(mode="after")
    def valid(self) -> Self:
        from wealthlab.products.life_illustration_validation import validate

        validate(self)
        return self


class LifeStudy(TaxModel):
    synthetic: bool
    retirement_date: date | None
    insurance_need: Money | None
    illustrations: list[LifeIllustration] = Field(min_length=1)

    @model_validator(mode="after")
    def unique(self) -> Self:
        ids = [item.id for item in self.illustrations]
        if len(set(ids)) != len(ids):
            raise ValueError("Illustration IDs must be unique.")
        return self
