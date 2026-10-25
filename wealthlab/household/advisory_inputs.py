"""Sourced outer cash fees declare rate methods, period factors and observed valuation scope.

Nondefault interpretations require separate source confirmation at execution.
An annual day count may be unknown only when every period supplies a fixed factor.
"""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.tax.facts import TaxModel

Rate = Annotated[Decimal, Field(ge=0, le=1)]


class AdvisoryTier(TaxModel):
    upper_limit: Money | None
    annual_rate: Rate


class AdvisoryCoverage(TaxModel):
    account_id: Identifier
    value_basis: Literal[
        "modeled_net_account_equity", "life_net_cash_value", "life_net_surrender_value"
    ]
    presence: Literal["required", "if_present"] = "required"
    absence_permitted_by_source_confirmed: bool = False


class AdvisoryPeriod(TaxModel):
    fixed_annual_period_fraction: Annotated[Decimal, Field(gt=0, le=1)] | None = None
    fixed_fraction_source_confirmed: bool = False
    accrual_start: date
    accrual_end: date
    valuation_date: date
    assessment_date: date
    payment_due_date: date
    valuation_cutoff: Literal[
        "product_marks_before_optional_saving", "opening", "completed_month_end"
    ] = "product_marks_before_optional_saving"


class AdvisorySchedule(Record):
    source_ref: str = Field(min_length=1, max_length=500)
    source_date: date
    available_on: date
    contract_terms_and_valuation_basis_confirmed: bool
    outer_cash_fee_not_already_in_embedded_costs_confirmed: bool
    covered: list[AdvisoryCoverage] = Field(min_length=1)
    tiers: list[AdvisoryTier] = Field(min_length=1)
    rate_application: Literal["progressive_marginal", "whole_relationship_breakpoint"] = (
        "progressive_marginal"
    )
    whole_relationship_breakpoints_source_confirmed: bool = False
    advance_nonrefundable_no_proration_assumed_confirmed: bool = False
    fixed_per_period: Money = Decimal(0)
    day_count: Literal[365, 366, 360] | None = None
    periods: list[AdvisoryPeriod] = Field(min_length=1)


class AdvisoryPlan(TaxModel):
    valuation_timing: Literal[
        "observed_product_marks_before_optional_saving_and_deposits",
        "explicit_observed_snapshot_cutoffs",
    ]
    payment_scope: Literal["household_cash_pool"]
    payment_account_ids: list[Identifier] = Field(min_length=1)
    schedules: list[AdvisorySchedule] = Field(min_length=1)
