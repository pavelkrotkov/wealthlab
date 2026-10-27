"""Dated person-specific NJ tax status and independently classified state source facts.

These are conditional legal facts, not residence inferred from an address or
from federal citizenship. Exclusive ends match the household calendar. Income
amounts retain NJ basis/classification independently of federal recognition.
"""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money
from wealthlab.tax.facts import SignedMoney, TaxModel
from wealthlab.tax.nj_facts import NJDeductions


class NJResidencePeriod(TaxModel):
    start: date
    end: date


class NJPersonResidence(TaxModel):
    id: Identifier
    role: Literal["primary", "spouse"]
    status: Literal["full_year", "part_year", "nonresident", "unresolved"]
    periods: list[NJResidencePeriod]
    residency_facts_assumed_confirmed: bool
    us_citizen_full_year_assumed_confirmed: bool
    source: str = Field(min_length=1, max_length=500)


class NJSourceIncome(TaxModel):
    id: Identifier
    owner_id: Identifier
    received: date
    kind: Literal["wages", "interest", "dividends", "dispositions", "pension", "other"]
    amount: SignedMoney
    nj_source: Literal["allowed", "denied", "unresolved"]
    amount_and_classification_assumed_confirmed: bool
    source: str = Field(min_length=1, max_length=500)


class NJPeriodDeductions(TaxModel):
    owners: list[Identifier] = Field(min_length=1, max_length=2)
    period: Literal["resident", "nonresident"]
    paid_on: date
    inputs: NJDeductions
    eligibility_and_period_allocation_assumed_confirmed: bool
    source: str = Field(min_length=1, max_length=500)


class NJResidencePlan(TaxModel):
    as_of: date
    people: list[NJPersonResidence] = Field(min_length=1, max_length=2)
    income: list[NJSourceIncome]
    deductions: list[NJPeriodDeductions] = Field(default_factory=list)
    actual_payments_by_return: dict[str, Money] = Field(default_factory=dict)
    filing_election: Literal[
        "follow_federal", "mixed_spouse_separate", "one_nonresident_source_separate"
    ] = "follow_federal"
    filing_election_assumed_confirmed: bool
    retirement_exclusions: Literal["allowed", "denied", "unresolved"] = "unresolved"
    source: str = Field(min_length=1, max_length=500)
