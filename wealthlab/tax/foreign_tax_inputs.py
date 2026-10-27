"""Foreign assessments and planned settlements share the existing household USD wallet.

Assessments are supplied conditional liabilities, not payments or residence
conclusions. Their revisions retain the original identity. Dated settlement
quotes, schedules and actually linked source withholding stay independent.
"""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.foreign_credit_inputs import Claim, CreditTaxCash, ForeignCreditCase, Rate

Fraction = Annotated[Decimal, Field(ge=0, le=1)]


class ForeignAssessment(TaxModel):
    id: Identifier
    owner_id: Identifier
    country: str = Field(pattern=r"^[A-Z]{2}$")
    liability_year: int = Field(ge=1900, le=2145)
    tax_type: Literal["income", "wealth", "social", "other"]
    currency: Literal["USD", "EUR"]
    observed: date
    amount_native: Money
    eligibility: Claim
    refund_claim_eligibility: Claim = "unresolved"
    source: str = Field(min_length=1, max_length=500)


class ForeignAssessmentRevision(TaxModel):
    assessment_id: Identifier
    observed: date
    amount_native: Money
    source: str = Field(min_length=1, max_length=500)


class ForeignSettlementQuote(TaxModel):
    date: date
    currency: Literal["USD", "EUR"]
    usd_per_unit: Rate
    source: str = Field(min_length=1, max_length=500)


class ForeignPaymentSchedule(TaxModel):
    id: Identifier = Field(max_length=50)
    assessment_id: Identifier
    due_date: date
    requested_native: Money
    fee_per_execution_usd: Money = Decimal(0)
    basket: Literal["general", "passive", "treaty_resourced", "unknown"]
    creditable_fraction: Fraction
    credit_eligibility: Claim
    included_income_confirmed: bool
    source_income_year: int | None = Field(default=None, ge=1900, le=2145)
    income_ids: list[Identifier] = Field(default_factory=list)
    source: str = Field(min_length=1, max_length=500)


class ForeignObservedTax(TaxModel):
    assessment_id: Identifier
    source_income_year: int | None = Field(default=None, ge=1900, le=2145)
    record: CreditTaxCash


class ForeignTaxPlan(TaxModel):
    assessments: list[ForeignAssessment] = Field(min_length=1)
    revisions: list[ForeignAssessmentRevision] = Field(default_factory=list)
    schedules: list[ForeignPaymentSchedule]
    quotes: list[ForeignSettlementQuote] = Field(min_length=1)
    opening_payments: list[ForeignObservedTax] = Field(default_factory=list)
    source_withholding: list[ForeignObservedTax] = Field(default_factory=list)
    refunds: list[ForeignObservedTax] = Field(default_factory=list)
    credit_profiles: list[ForeignCreditCase] = Field(min_length=1)
    allow_household_sales: bool = False
    source: str = Field(min_length=1, max_length=500)
