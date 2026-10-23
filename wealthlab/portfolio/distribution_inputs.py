"""Distribution cash dates, tax character and issuer eligibility are separate assumptions."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Record
from wealthlab.portfolio.models import Price


class Distribution(Record):
    security_id: str
    ex_date: date
    payment_date: date
    recognition_date: date
    per_share: Price
    federal_character: Literal["dividends", "interest", "tax_exempt_interest", "long_term"]
    nj_character: Literal["dividends", "interest", "dispositions", "exempt"]
    qualified_fraction: Annotated[Decimal, Field(ge=0, le=1)] = Decimal(0)
    qualified_issuer_confirmed: bool = False
    undiminished_risk_confirmed: bool = False

    @model_validator(mode="after")
    def dates_and_character(self) -> Self:
        if min(self.payment_date, self.recognition_date) < self.ex_date:
            raise ValueError("Cash receipt and tax recognition cannot precede entitlement.")
        if self.qualified_fraction and self.federal_character != "dividends":
            raise ValueError("Only ordinary dividends contain a qualified dividend component.")
        return self
