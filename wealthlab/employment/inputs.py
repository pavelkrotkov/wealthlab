"""Explicit salary/bonus stream choices; job changes do not rewrite opening YTD wages."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Record
from wealthlab.tax.facts import TaxModel

Multiplier = Annotated[Decimal, Field(ge=0, le=10, max_digits=9, decimal_places=6)]


class WageChange(Record):
    date: date
    kind: Literal["pay_change", "job_loss", "return_to_work"]
    multiplier: Multiplier


class WagePath(Record):
    owner: Identifier
    income_ids: list[Identifier] = Field(min_length=1)
    opening_multiplier: Multiplier
    changes: list[WageChange]


class EmploymentPlan(TaxModel):
    paths: list[WagePath] = Field(min_length=1)
