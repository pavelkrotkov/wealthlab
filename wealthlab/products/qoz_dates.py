"""Monthly cash conventions constrain the supported statutory investment clocks.

Calls enter at month end, after real source sales; they earn no earlier return.
Leap-day contributions and thirty-year cap observations require another adapter.
Each call keeps its own investment date instead of tacking the source holding period.
"""


def validate_dates(scenario, plan, expected):
    validate_month_boundaries(scenario)
    dates = [c.date for c in plan.calls] + [plan.sale_requested, plan.sale_not_before]
    if any(when not in expected or (when.month, when.day) == (2, 29) for when in dates):
        raise ValueError("QOZ calls/sale dates must be observed month ends, excluding leap day.")
    if any(c.date >= plan.sale_requested for c in plan.calls):
        raise ValueError("Capital calls must precede the full-interest sale request.")
    validate_records(plan)
    validate_horizon(scenario, plan)
    validate_inclusion_marks(scenario, plan, expected)


def validate_records(plan):
    identities = [c.id for c in plan.calls] + [o.id for o in plan.observations]
    if len(set(identities)) != len(identities):
        raise ValueError("QOZ call and observation identities must be unique.")
    if any(r.provenance == "unresolved" for r in [*plan.calls, *plan.observations]):
        raise ValueError("Resolve QOZ call and observation provenance.")


def validate_horizon(scenario, plan):
    if min(c.date for c in plan.calls).year < 2026:
        raise ValueError(
            "This adapter supports new investments from 2026, not legacy opening interests."
        )
    if any(
        c.date.year > 2026 and c.date.replace(year=c.date.year + 30) < scenario.end
        for c in plan.calls
    ):
        raise ValueError("Thirty-year FMV-cap observations require another QOZ profile.")


def validate_inclusion_marks(scenario, plan, expected):
    from wealthlab.products.qoz_tax import inclusion_date

    due = [inclusion_date(c.date) for c in plan.calls]
    if any(scenario.start <= when < scenario.end and when not in expected for when in due):
        raise ValueError("Statutory QOZ inclusion needs an exact observed month-end FMV.")


def validate_month_boundaries(scenario):
    if scenario.start.day != 1 or scenario.end.day != 1:
        raise ValueError("QOZ requires whole calendar months beginning/ending on the first.")
