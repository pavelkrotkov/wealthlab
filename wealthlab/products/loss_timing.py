"""Conditional recognition assumptions do not decide legal eligibility or adjust tax basis."""

from datetime import date
from typing import Literal, Self

from pydantic import model_validator

from wealthlab.tax.facts import TaxModel


class LossTiming(TaxModel):
    treatment: Literal["allowed", "denied", "deferred"] = "allowed"
    release_on: date | None = None
    eligibility_after_limits_assumed: bool = False

    @model_validator(mode="after")
    def release_matches_treatment(self) -> Self:
        if (self.treatment == "deferred") != (self.release_on is not None):
            raise ValueError("Only deferred losses require an explicit assumed release date.")
        return self
