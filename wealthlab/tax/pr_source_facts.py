"""Independent recognized amounts and source claims for each annual receipt."""

from datetime import date
from decimal import Decimal
from typing import Literal, Self

from pydantic import model_validator

from wealthlab.household.records import Money
from wealthlab.tax.facts import TaxModel


class SourceIncome(TaxModel):
    received: date
    owner: Literal["primary", "spouse"] = "primary"
    kind: Literal["wages", "interest", "dividends", "ordinary", "long_term"]
    federal_amount: Money
    pr_amount: Money
    qualified_dividends: Money = Decimal(0)
    federal_source: Literal["PR", "US", "unset"] = "unset"
    pr_source: Literal["PR", "US", "unset"] = "unset"
    us_government_wages: bool = False
    evidence: str = ""

    @model_validator(mode="after")
    def components(self) -> Self:
        if self.qualified_dividends > self.federal_amount:
            raise ValueError("Qualified dividends are included in federal dividends.")
        if self.kind != "dividends" and self.qualified_dividends:
            raise ValueError("Only dividend rows can contain qualified dividends.")
        if self.kind != "wages" and self.us_government_wages:
            raise ValueError("US-government service exception requires a wage row.")
        return self
