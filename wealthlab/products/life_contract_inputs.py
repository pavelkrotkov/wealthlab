"""Executed policy events and explicitly conditional contract tax assumptions."""

from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Money, Record
from wealthlab.products.life_contract_records import PolicyEvent
from wealthlab.products.life_illustration_records import LifeValue
from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.facts import TaxModel


class LifeContract(Record):
    name: str = Field(min_length=1, max_length=120)
    source: str = Field(min_length=1, max_length=500)
    source_date: date
    start: date
    issue_date: date
    owner_birth_date: date
    opening_federal_basis: Money | None
    opening_loan: Money
    federal_status: Literal["non_mec", "mec", "unknown"]
    ordinary_personal_contract_confirmed: bool
    no_aggregation_or_special_basis_adjustments_confirmed: bool
    withdrawals_without_early_benefit_recapture_confirmed: bool
    capitalized_interest_is_new_loan_confirmed: bool
    additional_tax_exception: Literal["none", "disability_confirmed", "sepp_confirmed"]
    values_match_executed_events_confirmed: bool
    stop_funding_date: date | None
    events: list[PolicyEvent] = Field(default_factory=list)
    values: list[LifeValue] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid(self) -> Self:
        from wealthlab.products.life_contract_validation import validate

        validate(self)
        return self


class LifeContractCase(TaxModel):
    synthetic: bool
    contract: LifeContract
    insurance_need: Money | None
    retirement_date: date | None
    annual_cases: dict[int, AnnualCase] = Field(default_factory=dict)
    currency: Literal["USD"] = "USD"
