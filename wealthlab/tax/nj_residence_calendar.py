"""Count legal resident and nonresident months independently under the 15-day rule.

Physical travel does not determine these declared tax-residence periods. A
31-day split may count a month on both returns; no invented 12-month combined
cap replaces the official separate resident/nonresident proration rules.
"""

from calendar import monthrange
from datetime import date, timedelta


def year_days(year):
    first, following = date(year, 1, 1), date(year + 1, 1, 1)
    return {first + timedelta(days=i) for i in range((following - first).days)}


def resident_days(person, year):
    result = set()
    for period in sorted(person.periods, key=lambda p: p.start):
        if not date(year, 1, 1) <= period.start < period.end <= date(year + 1, 1, 1):
            raise ValueError(
                "NJ residence periods require valid exclusive dates inside the tax year."
            )
        days = {period.start + timedelta(days=i) for i in range((period.end - period.start).days)}
        if result & days:
            raise ValueError("A person's NJ residence periods cannot overlap.")
        result.update(days)
    return result


def months(days, year):
    return sum(
        sum(date(year, month, day) in days for day in range(1, monthrange(year, month)[1] + 1))
        >= 15
        for month in range(1, 13)
    )


def validate_status(person, days, year):
    full = year_days(year)
    expected = "full_year" if days == full else "part_year" if days else "nonresident"
    if person.status != expected:
        raise ValueError(
            "Declared NJ status must match the supplied complete legal residence periods."
        )
    if not person.residency_facts_assumed_confirmed:
        raise ValueError(
            "Confirm NJ legal residence facts; travel dates alone do not establish status."
        )
