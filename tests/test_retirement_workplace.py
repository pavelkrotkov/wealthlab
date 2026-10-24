"""Published workplace caps vary by age, year and prior sponsor wages."""

import pytest
from test_retirement_contributions import calculate, case_for


@pytest.mark.parametrize(
    ("birth", "prior", "permitted", "expected"),
    [
        ("1980-06-15", "200000.00", True, 24500),
        ("1976-06-15", "150000.00", True, 32500),
        ("1976-06-15", "150000.01", True, 24500),
        ("1966-06-15", "150000.00", True, 35750),
        ("1963-06-15", "150000.00", True, 35750),
        ("1962-06-15", "150000.00", True, 32500),
        ("1965-06-15", "150000.00", False, 24500),
    ],
)
def test_2026_age_plan_and_same_employer_wage_threshold(birth, prior, permitted, expected):
    data = case_for(
        "pretax_401k", birth_date=birth, prior_employer_wages=prior, catchup_permitted=permitted
    )
    assert calculate(data)["orders"][0]["funded"] == expected


def test_2025_does_not_inherit_2026_roth_requirement():
    data = case_for("pretax_401k")
    data["year"] = 2025
    data["orders"][0]["date"] = "2025-01-15"
    assert calculate(data)["orders"][0]["funded"] == 34750
