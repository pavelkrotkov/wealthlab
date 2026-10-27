"""Independently permitted credits enter the existing native federal credit order.

These are supplied tax facts, not an eligibility or Form1116 determination.
An explicit AMT computation keeps regular FTC from becoming an unstated AMT
credit under Tax-Calculator's no-Form6251 shortcut. No filing action is inferred.
"""

from decimal import Decimal
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Money
from wealthlab.tax.facts import TaxModel


class ForeignCredits(TaxModel):
    regular: Money = Decimal(0)
    alternative_minimum: Money = Decimal(0)
    eligibility: Literal["allowed", "denied", "unresolved"] = "unresolved"
    source: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def validate_source(self) -> Self:
        if (self.regular or self.alternative_minimum) and (
            self.eligibility == "unresolved" or not self.source
        ):
            raise ValueError("Positive foreign credit facts need resolved eligibility and source.")
        return self

    def native(self, scale):
        if self.eligibility != "allowed":
            return {}
        return dict(
            e07300=float(self.regular) / scale,
            e62900=float(self.alternative_minimum) / scale,
            f6251=1,
        )
