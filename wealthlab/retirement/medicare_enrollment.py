"""Confirm coverage parts and whole-month enrollment without inferring eligibility.

Part A eligibility can precede age 65; turning 65 alone does not establish
enrollment. This engine therefore requires explicit confirmed coverage dates.
Only standard full Part B is supported. Hold-harmless and specialized benefits
must not silently become standard-premium calculations.
"""

from datetime import date
from itertools import pairwise

from wealthlab.retirement.medicare_history import income_for


def validate_coverage(case, item, members):
    if item.member not in members or not item.eligibility_confirmed:
        raise ValueError("Medicare enrollment requires a known member and confirmed eligibility.")
    start, end = date(case.start_year, 1, 1), date(case.end_year, 1, 1)
    if not start <= item.start < item.end <= end or item.start.day != 1 or item.end.day != 1:
        raise ValueError("Medicare coverage must use first-of-month dates within the projection.")
    validate_parts(item)


def validate_overlaps(case):
    for member in case.members:
        periods = sorted((c.start, c.end) for c in case.coverage if c.member == member.id)
        if any(right[0] < left[1] for left, right in pairwise(periods)):
            raise ValueError("A member's Medicare coverage periods cannot overlap.")


def validate_income_coverage(case):
    for coverage in case.coverage:
        if coverage.part_b or coverage.part_d:
            for year in range(coverage.start.year, coverage.end.year + 1):
                if date(year, 1, 1) < coverage.end and date(year + 1, 1, 1) > coverage.start:
                    income_for(case, coverage.member, year)


def validate_parts(item):
    if not any((item.part_a, item.part_b, item.part_d)):
        raise ValueError("Select at least one Medicare coverage part.")
    if (not item.part_a and item.part_a_monthly_2026) or (
        not item.part_d and item.part_d_plan_monthly_2026
    ):
        raise ValueError("Unenrolled Medicare parts cannot charge a plan premium.")
    if item.part_b and not item.standard_b_premium_applicable:
        raise ValueError(
            "Confirm standard full Part B; hold-harmless/special coverage needs another model."
        )
