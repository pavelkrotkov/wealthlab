"""Dated citizenship, tax-home and local-residence claims are supplied independently."""

from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.tax.facts import TaxModel

Claim = Literal["confirmed", "assumed", "unset", "fails"]


class Residence(TaxModel):
    us_citizen: Claim = "unset"
    federal_bfr: Literal["full_year", "move_in", "move_out", "no", "unset"] = "unset"
    presence_days: int = Field(default=0, ge=0, le=366)
    tax_home: Claim = "unset"
    closer_connection: Claim = "unset"
    prior_three_nonresident: Claim = "unset"
    next_three_resident: Claim = "unset"
    prior_two_resident: Claim = "unset"
    local_start: date | None = None
    local_end: date | None = None
    evidence: str = ""

    @model_validator(mode="after")
    def dates(self) -> Self:
        if self.local_start and self.local_end and self.local_start > self.local_end:
            raise ValueError("Local residence start must not follow its end.")
        return self
