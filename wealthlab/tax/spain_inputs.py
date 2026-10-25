"""One person, one calendar year and one explicitly supplied Spanish residence profile."""

from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier, Money
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.spain_income_records import SpanishIncome
from wealthlab.tax.spain_payment_records import SpanishTaxPayment
from wealthlab.tax.spain_records import (
    Source,
    SpanishAsset,
    SpanishCredits,
    SpanishDebt,
    SpanishWealthAllowance,
)


class SpainCase(TaxModel):
    synthetic: bool
    person_id: Identifier
    year: int = Field(ge=2025, le=2100)
    as_of: date
    policy: Literal["published_2025", "frozen_2025"]
    citizenship: Literal["us", "other", "unknown"]
    residence: Literal["full_year_resident", "nonresident", "special_regime", "unknown"]
    residence_source: Source
    region: str | None
    filing: Literal["individual", "joint", "unknown"]
    worldwide_inputs_complete_confirmed: bool
    recognition_prelimited_confirmed: bool
    incomes: list[SpanishIncome]
    general_reduction_eur: Money
    savings_reduction_eur: Money
    state_minimum_eur: Money
    regional_minimum_eur: Money
    allowance_source: Source
    assets: list[SpanishAsset]
    debts: list[SpanishDebt]
    long_held_gain_cap_exclusion_eur: Money
    patrimonial_company_dividends_eur: Money
    cap_adjustment_source: Source
    wealth_allowance: SpanishWealthAllowance | None = None
    credits: SpanishCredits
    payments: list[SpanishTaxPayment]

    @model_validator(mode="after")
    def validate_records(self) -> Self:
        from wealthlab.tax.spain_validation import validate

        validate(self)
        return self
