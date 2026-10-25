"""Dated policy histories preserve supplied same-day execution order.

A value is measured after every event on its date. The opening snapshot owns
all earlier basis and debt history; events cannot rewrite that prior period.
"""


def validate_events(events):
    if any(event.provenance == "unresolved" for event in events):
        raise ValueError("Executed policy events require resolved amounts and dates.")
    if len({e.id for e in events}) != len(events):
        raise ValueError("Policy event IDs must be unique.")
    if [e.date for e in events] != sorted(e.date for e in events):
        raise ValueError("Policy events must be in execution order; same-day list order applies.")


def validate_dates(contract):
    dates = [e.date for e in contract.events] + [v.date for v in contract.values]
    if any(d < contract.start for d in dates):
        raise ValueError("Policy events and values cannot precede the opening snapshot.")
    if [v.date for v in contract.values] != sorted({v.date for v in contract.values}):
        raise ValueError("Policy value dates must be unique and ordered.")
