"""Explicit amounts, currencies and dates; no inferred personal facts."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

Money = Annotated[Decimal, Field(ge=0, max_digits=18, decimal_places=2)]
Currency = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
Identifier = Annotated[str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    id: Identifier
    provenance: Literal["fact", "assumption", "illustration", "unresolved"]


class Member(Record):
    birth_date: date
    retirement_date: date

    @model_validator(mode="after")
    def dates(self) -> Self:
        if self.retirement_date <= self.birth_date:
            raise ValueError("Retirement date must follow birth date.")
        return self


class Account(Record):
    owner: Identifier
    currency: Currency
    wrapper: Literal[
        "cash",
        "taxable",
        "traditional",
        "roth",
        "hsa",
        "education",
        "property",
        "employer",
        "insurance",
    ]
    balance: Money
    monthly_fee: Money
