"""Explicit proportional-basis funding before the tax-lot strategy layer."""

from datetime import date
from decimal import Decimal
from typing import Literal

from wealthlab.household.records import Money
from wealthlab.tax.facts import TaxModel


class FundingSource(TaxModel):
    account_id: str
    federal_basis: Money
    nj_basis: Money
    federal_character: Literal["short_term", "long_term"]
    loss_treatment: Literal["allowed", "denied"]
    liquid_after: date


def recognized(value: Decimal, basis: Decimal, sold: Decimal, treatment: str) -> Decimal:
    from wealthlab.household.calendar import money

    gain = money(sold * (1 - basis / value))
    return max(Decimal(0), gain) if treatment == "denied" else gain
