"""Complete dated observations and declared tax paths are required for actual spending.

A future market binding must price all legs on the same realized stock/index
path. Carrying stale option values into a new path is never an implicit adapter.
"""

from datetime import timedelta

from wealthlab.household.calendar import months
from wealthlab.products.option_tax import unresolved


def validate_calendar(case, scenario):
    if scenario.start.day != 1 or scenario.end.day != 1:
        raise ValueError("Household options require complete calendar months.")
    if case.holdings.as_of != scenario.start or case.holdings.end != scenario.end - timedelta(
        days=1
    ):
        raise ValueError(
            "Option dates must cover the exact household horizon through its last day."
        )
    dates = {mark.date for mark in case.marks}
    if any(end - timedelta(days=1) not in dates for _, end in months(scenario.start, scenario.end)):
        raise ValueError("Every household month needs an explicit final-day accounting mark.")


def validate_tax(case):
    missing = unresolved(case.tax, "federal") + unresolved(case.tax, "nj")
    if missing or any(leg.federal_class == "unresolved" for leg in case.legs):
        raise ValueError("Resolve federal/NJ option tax assumptions before household funding.")
