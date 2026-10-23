"""Versioned scenario validation and explicit first-year opening context."""

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlab.household.records import Account, Member, Money
from wealthlab.household.schedules import Contribution, Debt, Expense, Income
from wealthlab.household.validation import validate_dates, validate_references


class YearToDate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    gross_income: Money
    federal_tax_paid: Money
    state_tax_paid: Money


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    schema_version: Literal[1]
    name: str = Field(min_length=1, max_length=120)
    synthetic: bool
    start: date
    end: date
    inflation: float = Field(ge=-0.5, le=1)
    usd_per_currency: dict[str, Annotated[float, Field(gt=0, le=1000000)]]
    reserve_years: float = Field(ge=0, le=20)
    target_success: float = Field(gt=0, le=1)
    target_age: int = Field(ge=50, le=120)
    ytd: YearToDate
    members: list[Member] = Field(min_length=1, max_length=2)
    accounts: list[Account] = Field(min_length=1)
    incomes: list[Income]
    expenses: list[Expense]
    debts: list[Debt]
    contributions: list[Contribution]

    @model_validator(mode="after")
    def validate_inputs(self) -> Self:
        validate_dates(self)
        validate_references(self)
        return self
