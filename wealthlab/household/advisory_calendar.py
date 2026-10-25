"""Dated arrears assessment never changes the supplied accrual span or invents prior marks."""

from datetime import timedelta


def validate_periods(scenario, schedule):
    previous = None
    for period in schedule.periods:
        if not scenario.start <= period.accrual_start <= period.accrual_end <= scenario.end:
            raise ValueError("Advisory accrual dates must lie inside the projection.")
        validate_stage(scenario, period)
        if previous is not None and (
            period.accrual_start < previous.accrual_end
            or period.assessment_date <= previous.assessment_date
        ):
            raise ValueError("Advisory periods must be ordered and cannot overlap or repeat.")
        previous = period


def validate_stage(scenario, period):
    when = period.assessment_date
    if not scenario.start <= when < scenario.end or (when + timedelta(days=1)).day != 1:
        raise ValueError("Advisory assessments require an actual modeled month-end date.")
    if (period.valuation_date, period.payment_due_date) != (when, when):
        raise ValueError("This advisory stage requires same-date observed valuation and due date.")
    if period.accrual_end > when + timedelta(days=1):
        raise ValueError("Advance advisory billing requires a separate dated snapshot profile.")
