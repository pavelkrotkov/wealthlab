"""SSA's full-month age62 rule differs from attainment of FRA and age70."""

from datetime import date

import pytest

from wealthlab.retirement.social_dates import (
    earliest_retirement_month,
    full_retirement_month,
    seventieth_month,
)


@pytest.mark.parametrize(
    ("birth", "earliest", "fra", "seventy"),
    [
        ("1960-01-01", "2022-01-01", "2026-10-01", "2029-12-01"),
        ("1960-01-02", "2022-01-01", "2027-01-01", "2030-01-01"),
        ("1960-01-03", "2022-02-01", "2027-01-01", "2030-01-01"),
        ("1959-12-31", "2022-01-01", "2026-10-01", "2029-12-01"),
    ],
)
def test_birth_day_and_cohort_bridge_to_actual_months(birth, earliest, fra, seventy):
    birth = date.fromisoformat(birth)
    assert earliest_retirement_month(birth) == date.fromisoformat(earliest)
    assert full_retirement_month(birth) == date.fromisoformat(fra)
    assert seventieth_month(birth) == date.fromisoformat(seventy)
