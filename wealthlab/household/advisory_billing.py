"""Conditional sourced rate/fraction choices never alter actual observation or cash dates.

Upper limits are inclusive for whole-relationship breakpoints; a selected rate
applies to the complete eligible base, not only its excess above a threshold.
Fixed annual fractions are supplied contract inputs, never inferred proration.
"""

from decimal import Decimal

from wealthlab.household.calendar import money


def validate(schedule):
    if schedule.rate_application == "whole_relationship_breakpoint" and not (
        schedule.whole_relationship_breakpoints_source_confirmed
    ):
        raise ValueError(
            "Whole-relationship rates need sourced inclusive breakpoint interpretation."
        )
    for period in schedule.periods:
        if (
            period.fixed_annual_period_fraction is not None
        ) != period.fixed_fraction_source_confirmed:
            raise ValueError(
                "Supply a fixed annual period fraction and source confirmation together."
            )
        if period.fixed_annual_period_fraction is None and schedule.day_count is None:
            raise ValueError("Actual-day advisory billing requires a supplied annual day count.")


def breakpoint_charge(base, tiers):
    lower = Decimal(0)
    for tier in tiers:
        if tier.upper_limit is None or base <= tier.upper_limit:
            return base * tier.annual_rate, dict(
                lower=lower,
                upper=tier.upper_limit,
                upper_limit_inclusive=True,
                base=base,
                rate=tier.annual_rate,
            )
        lower = tier.upper_limit
    raise ValueError("Whole-relationship rates require a final unlimited breakpoint.")


def variable_charge(annual, schedule, period):
    fraction = period.fixed_annual_period_fraction
    if fraction is None:
        # Preserve the original multiplication/division order before currency rounding.
        days = (period.accrual_end - period.accrual_start).days
        return money(annual * days / schedule.day_count)
    return money(annual * fraction)


def period_terms(schedule, period):
    fixed = period.fixed_annual_period_fraction
    return dict(
        period_factor_basis=(
            "actual_days_over_day_count" if fixed is None else "supplied_fixed_annual_fraction"
        ),
        fixed_annual_period_fraction=fixed,
        applied_day_count=schedule.day_count if fixed is None else None,
    )
