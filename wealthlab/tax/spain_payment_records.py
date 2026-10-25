"""Observed cash settlements are independent of assessed liabilities and credit translation."""

from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.spain_money import SpanishAmount


class SpanishTaxPayment(TaxModel):
    """Observed cash is separate from an assessment and keeps its own FX/date."""

    id: Identifier
    owner_id: Identifier
    liability_year: int = Field(ge=2025, le=2100)
    tax_type: Literal["irpf", "wealth", "solidarity"]
    kind: Literal["payment", "withholding", "refund"]
    value: SpanishAmount
    recognized_tax_eur: Money
    tax_recognition_source: str = Field(min_length=1, max_length=500)
    reverses_id: Identifier | None = None
