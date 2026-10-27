"""Explicit monthly billing cutoffs preserve advance accrual spans without inventing prior marks.

Daily/first-day billing is outside this profile. A source-confirmed future
service span does not permit future valuation data or an earlier cash receipt.
Refund/proration terms are supplied independently of the charged accrual days.
"""

from datetime import timedelta


def validate_periods(scenario, schedule):
    previous = None
    for period in schedule.periods:
        if not scenario.start <= period.accrual_start <= period.accrual_end <= scenario.end:
            raise ValueError("Advisory accrual dates must lie inside the projection.")
        validate_stage(scenario, period, schedule)
        if previous is not None and (
            period.accrual_start < previous.accrual_end
            or period.assessment_date <= previous.assessment_date
        ):
            raise ValueError("Advisory periods must be ordered and cannot overlap or repeat.")
        previous = period


def validate_stage(scenario, period, schedule):
    when = period.assessment_date
    if not scenario.start <= when < scenario.end or (when + timedelta(days=1)).day != 1:
        raise ValueError("Advisory assessments require an actual modeled month-end date.")
    if period.payment_due_date != when:
        raise ValueError("This advisory stage requires same-date month-end billing and due date.")
    validate_valuation(scenario, period)
    if period.accrual_end > when + timedelta(days=1) and not (
        schedule.advance_nonrefundable_no_proration_assumed_confirmed
    ):
        raise ValueError(
            "Advance advisory billing requires sourced nonrefundable/no-proration terms."
        )


def validate_valuation(scenario, period):
    legacy = scenario.advisory_fee_plan.valuation_timing != "explicit_observed_snapshot_cutoffs"
    if legacy and (period.valuation_date, period.valuation_cutoff) != (
        period.assessment_date,
        "product_marks_before_optional_saving",
    ):
        raise ValueError("This advisory stage requires same-date observed valuation.")
    if not scenario.start <= period.valuation_date <= period.assessment_date:
        raise ValueError(
            "Advisory valuation needs an available past snapshot, never a future date."
        )
