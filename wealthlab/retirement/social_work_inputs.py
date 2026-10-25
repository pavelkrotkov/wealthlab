"""Reported forecasts and realized earned wages have different information dates."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.tax.facts import TaxModel


class WorkYear(Record):
    year: int = Field(ge=2026, le=2200)
    member: Identifier
    forecast_monthly_wages: list[Money] = Field(min_length=12, max_length=12)
    actual_monthly_wages: list[Money] | None = Field(default=None, min_length=12, max_length=12)


class WorkPolicy(TaxModel):
    years: list[WorkYear] = Field(min_length=1)
    grace_used_before_projection: dict[Identifier, bool]
    rule_mode: Literal["frozen_2026_us_w2_annual_and_monthly_tests"]
    closed_year_payment_month: int = Field(ge=1, le=12)
    arf_payment_month_following_fra_year: int = Field(ge=1, le=12)
    overpayment_recovery_fraction: Annotated[Decimal, Field(gt=0, le=1, decimal_places=6)]
    complete_current_us_w2_wages_without_special_payments_confirmed: bool
    no_prior_unmodeled_work_positions_or_reduction_credits_confirmed: bool
    no_auxiliary_work_effects_in_this_profile_confirmed: bool
    administrative_payment_timing_and_recovery_are_conditional_confirmed: bool
    no_special_lump_sum_tax_election_assumed: bool
