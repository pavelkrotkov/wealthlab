"""Declared inputs for a bounded optional OWL/household comparison.

One living single retiree, full calendar years, cash investments and a locked
conversion policy make both engines' account books representable. NJ principal
is supplied independently: this case is not an inference about a real IRA.
The reference is an accounting/forecast comparison, not a recommendation.
"""

from datetime import date
from decimal import Decimal
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Money
from wealthlab.tax.facts import TaxModel


class OwlHouseholdCase(TaxModel):
    start_year: int = Field(ge=2025, le=2036)
    years: int = Field(default=3, ge=2, le=11)
    age: int = Field(default=70, ge=65, le=100)
    cash: Money = Decimal(20000)
    traditional_ira: Money = Decimal(200000)
    roth_ira: Money = Decimal(0)
    federal_ira_basis: Money = Decimal(0)
    nj_ira_basis: Money = Decimal(200000)
    roth_first_year: int | None = Field(default=None, ge=1998, le=2036)
    annual_spending: Money = Field(default=Decimal(30000), gt=0)
    heirs_tax_rate: Decimal = Field(default=Decimal("0.30"), ge=0, le=1)
    birth_1959_start_age: Literal[73] | None = None
    synthetic: bool

    @model_validator(mode="after")
    def scope(self) -> Self:
        if self.start_year != date.today().year:
            raise ValueError(
                "This installed OWL Plan reference must start in the actual current year."
            )
        if self.start_year + self.years - 1 > 2036:
            raise ValueError(
                "The reference cannot exceed the installed federal package-law horizon."
            )
        if self.start_year - self.age == 1959 and self.birth_1959_start_age != 73:
            raise ValueError(
                "This OWL comparison needs explicit conditional age-73 for birth 1959."
            )
        validate_basis(self)
        return self


def validate_basis(case):
    if case.federal_ira_basis:
        raise ValueError("The OWL reference does not model nondeductible federal IRA basis.")
    if case.nj_ira_basis != case.traditional_ira:
        raise ValueError(
            "This federal reference requires explicitly full previously-taxed NJ IRA principal."
        )
    if case.roth_ira and (
        case.roth_first_year is None or case.start_year < case.roth_first_year + 5
    ):
        raise ValueError("Supply a completed five-year history for this qualified-Roth reference.")


def synthetic():
    return OwlHouseholdCase(start_year=date.today().year, synthetic=True)
