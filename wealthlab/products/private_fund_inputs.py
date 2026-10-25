"""Conditional cash-only private-fund terms; sponsor and tax conclusions are supplied inputs."""

from datetime import date
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Money, Record
from wealthlab.products.long_short_inputs import Rate
from wealthlab.products.loss_timing import LossTiming
from wealthlab.tax.facts import SignedMoney


class BasisAdjustment(Record):
    date: date
    federal: SignedMoney
    new_jersey: SignedMoney
    explanation: str = Field(min_length=1, max_length=1000)


class FundRequest(Record):
    notice_date: date
    amount: Money
    complete_liquidation: bool = False


class PrivateFundContract(Record):
    source_description: str = Field(min_length=1, max_length=1000)
    eligibility_assumed_confirmed: bool
    limited_liability_no_calls_assumed_confirmed: bool
    cash_only_no_hot_assets_no_liability_changes_assumed_confirmed: bool
    tax_basis_schedule_complete_assumed_confirmed: bool
    lock_until: date
    dealing: Literal["monthly", "quarterly", "annually"]
    notice_days: int = Field(ge=0, le=3650)
    gate_fraction: Annotated[Rate, Field(gt=0)]
    settlement_days: int = Field(ge=0, le=3650)
    federal_opening_basis: Money
    new_jersey_opening_basis: Money
    federal_capital_character: Literal["short_term", "long_term"]
    federal_exit_loss: LossTiming = Field(default_factory=LossTiming)
    new_jersey_exit_loss: LossTiming = Field(default_factory=LossTiming)
    basis_adjustments: list[BasisAdjustment] = Field(default_factory=list)
    requests: list[FundRequest] = Field(default_factory=list)
