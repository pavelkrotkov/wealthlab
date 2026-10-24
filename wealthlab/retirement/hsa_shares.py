"""Married family allocations cannot exceed the same shared monthly base."""

from decimal import Decimal

from wealthlab.retirement.hsa_capacity import calendars, eligible


def validate_shares(case):
    coverage = calendars(case)
    for number in range(1, 13):
        covered = [values[number] for values in coverage.values() if eligible(values[number])]
        family = case.married and any(month.coverage == "family" for month in covered)
        validate_month_shares(covered, family)


def validate_month_shares(covered, family):
    if not family:
        if any(month.family_share is not None for month in covered):
            raise ValueError("Family shares apply only to eligible married family-coverage pools.")
        return
    shares = [month.family_share for month in covered]
    total = sum(value if value is not None else Decimal(1) / len(covered) for value in shares)
    if total > 1:
        raise ValueError("Married HSA family shares exceed the shared monthly contribution limit.")
