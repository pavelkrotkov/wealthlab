"""Actual household sleeve cash with complete dated observations and supplied tax assumptions."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Record
from wealthlab.products.long_short_inputs import LongShortCase
from wealthlab.products.loss_timing import LossTiming
from wealthlab.products.private_fund_inputs import PrivateFundContract
from wealthlab.tax.facts import FederalIncome, TaxModel
from wealthlab.tax.nj_facts import NJIncome

Mark = Annotated[Decimal, Field(gt=-1, le=10, max_digits=18, decimal_places=12)]
Yield = Annotated[Decimal, Field(ge=0, le=1, max_digits=18, decimal_places=12)]


class SleeveObservation(Record):
    date: date
    long_return: Mark
    short_return: Mark
    long_yield: Yield
    short_yield: Yield
    locked: bool


class SleeveAllocation(Record):
    date: date
    federal: FederalIncome
    new_jersey: NJIncome
    federal_loss: LossTiming = Field(default_factory=LossTiming)
    new_jersey_loss: LossTiming = Field(default_factory=LossTiming)


class HouseholdSleeve(Record):
    account_id: Identifier
    private_fund_contract: PrivateFundContract | None = None
    case: LongShortCase
    observations: list[SleeveObservation] = Field(min_length=1)
    allocations: list[SleeveAllocation] = Field(default_factory=list)
    all_tax_recognition_and_exit_assumptions_supplied_confirmed: bool


class SleevePlan(TaxModel):
    sleeves: list[HouseholdSleeve] = Field(min_length=1)
    other_tax_inputs_exclude_supplied_allocations_confirmed: bool
    actual_household_cash_confirmed: bool
    priority: Literal["after_prior_tax_arrears_before_wrapper_deposits_and_current_tax"]
