"""Monthly-only contribution budgets; no speculative last-month/testing-period benefit."""

from decimal import ROUND_FLOOR, Decimal

LIMITS = {2025: dict(self=4300, family=8550), 2026: dict(self=4400, family=8750)}


def eligible(month):
    return not any((month.disqualifying_coverage, month.medicare, month.claimable_dependent)) and (
        month.coverage != "none"
    )


def calendars(case):
    return {owner.id: {month.month: month for month in owner.months} for owner in case.owners}


def monthly_base(case, person, month, coverage):
    """Either spouse's family coverage creates a shared base for eligible spouses.

    A Medicare-ineligible spouse leaves the eligible spouse the whole family
    base; each owner's age-based catch-up is added separately afterwards.
    """
    own = coverage[person.id][month]
    if not eligible(own):
        return Decimal(0)
    covered = [values[month] for values in coverage.values() if eligible(values[month])]
    family = case.married and any(value.coverage == "family" for value in covered)
    if family:
        share = own.family_share if own.family_share is not None else Decimal(1) / len(covered)
        return Decimal(LIMITS[case.year]["family"]) * share
    return Decimal(LIMITS[case.year][own.coverage])


def budgets(case):
    coverage = calendars(case)
    result = {}
    for person in case.owners:
        base = sum(monthly_base(case, person, month, coverage) for month in range(1, 13)) / 12
        catchup = Decimal(0)
        if case.year - person.birth_date.year >= 55:
            count = sum(eligible(month) for month in person.months)
            catchup = Decimal(1000) * count / 12
        result[person.id] = (base + catchup).quantize(Decimal(".01"), rounding=ROUND_FLOOR)
    return result
