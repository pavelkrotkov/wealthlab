"""Dated ordinary-source facts keep tax-credit recognition separate from actual cash."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.calendar import money
from wealthlab.household.records import Identifier, Money
from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.facts import TaxModel

Basket = Literal["general", "passive", "treaty_resourced", "unknown"]
Claim = Literal["allowed", "denied", "unresolved"]
Rate = Annotated[Decimal, Field(gt=0, le=1000000, max_digits=24, decimal_places=12)]


class CreditAmount(TaxModel):
    """Native value and the dated USD-per-unit spot quote retain their own source."""

    date: date
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    amount: Money
    usd_per_unit: Rate
    fx_source: str = Field(min_length=1, max_length=500)

    def dollars(self):
        return money(self.amount * self.usd_per_unit)


class CreditIncome(TaxModel):
    """Recognized ordinary amounts link a stable person to a supplied source/basket.

    Historical rows retain original identities for later tax payment evidence.
    Their cash is never deposited by the annual credit calculator.
    """

    id: Identifier
    owner_id: Identifier
    country: str = Field(pattern=r"^[A-Z]{2}$")
    kind: Literal["wages", "interest", "dividends", "ordinary"]
    basket: Basket
    value: CreditAmount
    source_classification: str = Field(min_length=1, max_length=500)


class CreditTaxCash(TaxModel):
    """An observed payment or refund keeps liability year separate from cash date.

    Creditable native tax is independently prelimited after legal restrictions.
    Explicit fees affect cash while refunds retain an original-payment link.
    """

    id: Identifier
    owner_id: Identifier
    country: str = Field(pattern=r"^[A-Z]{2}$")
    liability_year: int = Field(ge=2025, le=2145)
    tax_type: Literal["income", "wealth", "social", "other"]
    kind: Literal["payment", "withholding", "refund"]
    basket: Basket
    value: CreditAmount
    fx_fee_usd: Money = Decimal(0)
    creditable_native: Money
    eligibility: Claim
    included_income_confirmed: bool
    income_ids: list[Identifier] = Field(default_factory=list)
    source: str = Field(min_length=1, max_length=500)
    reverses_id: Identifier | None = None
    fx_income_id: Identifier | None = None


class CreditCarry(TaxModel):
    """USD credit vintage retains its original owner/year instead of being refreshed."""

    id: Identifier
    owner_id: Identifier
    origin_year: int = Field(ge=2015, le=2145)
    basket: Basket
    available_usd: Money
    source: str = Field(min_length=1, max_length=500)


class ForeignCreditCase(TaxModel):
    """One annual filing unit with independently confirmed source and carry facts.

    Person eligibility, allocation and filing-history continuity remain explicit.
    Unreviewed prior carryback capacity cannot silently create a forward-only
    conclusion or a predicted cash refund.
    """

    synthetic: bool
    annual: AnnualCase
    as_of: date
    people: dict[Identifier, Literal["primary", "spouse"]] = Field(min_length=1, max_length=2)
    income: list[CreditIncome] = Field(min_length=1)
    tax_cash: list[CreditTaxCash]
    opening_carries: list[CreditCarry] = Field(default_factory=list)
    credit_method: Literal["paid"] = "paid"
    fx_income_treatment: Literal["included_in_annual_facts", "unresolved"] = "unresolved"
    eligibility: Claim = "unresolved"
    ordinary_source_and_tax_allocation_confirmed: bool
    passive_category_no_special_reclassification_confirmed: bool = False
    carry_filing_unit_continuity_confirmed: bool
    prior_year_carryback_capacity_reviewed_zero_confirmed: bool
    source: str = Field(min_length=1, max_length=500)
