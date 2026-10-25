"""Require complete month-end observations and resolved, uniquely identified contract sources.

An income allocation belongs to its actual cash/recognition month; moving only
a request date cannot silently move the corresponding supplied tax assumption.
"""

from datetime import timedelta

from wealthlab.household.calendar import months


def validate_records(scenario, plan):
    if scenario.start.day != 1 or scenario.end.day != 1:
        raise ValueError("Exchange execution requires complete calendar months.")
    ends = [end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)]
    if [o.date for o in plan.observations] != ends:
        raise ValueError("Exchange observations must cover all month ends in order.")
    validate_identity(plan)
    validate_event_dates(plan, ends)


def validate_identity(plan):
    records = [
        plan.source_lot,
        plan.source_security,
        *plan.basket,
        *(b.security for b in plan.basket),
        *plan.observations,
        *plan.requests,
        *allocations(plan),
    ]
    if len({r.id for r in records}) != len(records):
        raise ValueError("Exchange source, observation, request and allocation IDs must be unique.")
    if any(r.provenance == "unresolved" for r in records):
        raise ValueError("Resolve exchange provenance before calculation.")


def validate_event_dates(plan, ends):
    for record in [*plan.observations, *plan.requests]:
        if record.date not in ends:
            raise ValueError("Exchange requests require in-horizon month-end dates.")
    validate_allocation_dates(plan)
    if [r.date for r in plan.requests] != sorted(r.date for r in plan.requests):
        raise ValueError("Exchange requests must be date ordered.")


def validate_allocation_dates(plan):
    if any(o.allocation.date != o.date for o in plan.observations):
        raise ValueError("Distribution allocation date must match its observation.")
    if any(r.date != r.early_tax.date for r in plan.requests):
        raise ValueError("Early-redemption tax date must match its request.")


def allocations(plan):
    return [o.allocation for o in plan.observations] + [r.early_tax for r in plan.requests]
