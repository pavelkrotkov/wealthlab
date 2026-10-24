"""Dated sleeve sources must be complete, ordered and resolved before execution.

Every account shares household dates, while event/observation IDs remain
unique across the product plan. Redemption requests are known policies;
they cannot silently shift from their supplied month into another period.
"""

from datetime import timedelta

from wealthlab.household.calendar import months


def validate_records(plan):
    records = [
        r for s in plan.sleeves for r in [s, *s.observations, *s.allocations, *s.case.redemptions]
    ]
    if len({r.id for r in records}) != len(records):
        raise ValueError("Sleeve observation/allocation/policy IDs must be unique.")
    if any(r.provenance == "unresolved" for r in records):
        raise ValueError("Resolve sleeve assumptions before household execution.")


def validate_dates(sleeve, scenario):
    ends = [end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)]
    if [r.date for r in sleeve.observations] != ends:
        raise ValueError("Sleeve observations must cover each household month end in order.")
    if any(r.date not in ends for r in sleeve.case.redemptions):
        raise ValueError("Sleeve redemptions require in-horizon month ends.")
