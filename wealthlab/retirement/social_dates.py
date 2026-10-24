"""Bridge Owl's stable FRA table to actual SSA entitlement months, not approximate ages."""

from datetime import date


def shift(when, count):
    absolute = when.year * 12 + when.month - 1 + count
    return date(absolute // 12, absolute % 12 + 1, 1)


def distance(start, end):
    return (end.year - start.year) * 12 + end.month - start.month


def full_retirement_month(birth, survivor=False):
    try:
        from owlplanner.socialsecurity import getFRAs, getSurvivorFRAs
    except ImportError as error:
        raise ValueError("Install the benchmarks extra for the pinned Owl FRA table.") from error
    table = getSurvivorFRAs if survivor else getFRAs
    age = table([birth.year], [birth.month], [birth.day])[0]
    return shift(birth, round(float(age) * 12) - int(birth.day == 1))


def earliest_retirement_month(birth):
    # Must be 62 throughout the month. A first-day birthday attains 62 on the
    # preceding month's last day, still too late for that preceding whole month.
    return shift(birth, 62 * 12 + int(birth.day > 2))


def seventieth_month(birth):
    return shift(birth, 70 * 12 - int(birth.day == 1))


def alive(person, month):
    return person.death_date is None or month < shift(person.death_date, 0)


def earliest_survivor_month(birth):
    # Aged widow(er) eligibility is attained at60; it is not the age62 throughout-month rule.
    return shift(birth, 60 * 12 - int(birth.day == 1))
