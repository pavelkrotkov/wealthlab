"""Conditional value tranches with supplied tax allocations independent of cash elections."""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.employment.compensation_events import CompensationEvent
from wealthlab.household.records import Identifier, Money, Record
from wealthlab.retirement.account_liquidity import AccountLock
from wealthlab.tax.facts import TaxModel


class Tranche(Record):
    """Vested opening value belongs in the account; unvested value is contingent."""

    account: Identifier
    opening_vested: Money
    opening_unvested: Money
    liquid_from: date
    unvested_tax_cash_right_confirmed: bool
    vested_tax_cash_before_liquidity_confirmed: bool


class CompensationPlan(TaxModel):
    """This conditional model does not reconstruct basis or hypothetical exit tax."""

    tranches: list[Tranche] = Field(min_length=1)
    events: list[CompensationEvent]
    liquidity_locks: list[AccountLock] = Field(default_factory=list)
    tax_inputs_exclude_plan_events_confirmed: bool
    all_plan_tax_recognition_supplied_confirmed: bool
    tax_policy: Literal["supplied_allocations_independent_of_cash_elections"]
    return_convention: Literal["net_embedded_fees_external_account_fees_separate"]
