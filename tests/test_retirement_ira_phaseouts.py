"""IRA contribution permission and federal/NJ basis have independent boundaries."""

import pytest
from test_retirement_contributions import calculate, case_for


@pytest.mark.parametrize(
    ("magi", "expected"),
    [("153000.00", 7500), ("160500.00", 3750), ("167999.00", 200), ("168000.00", 0)],
)
def test_roth_ira_phaseout_boundaries_and_minimum(magi, expected):
    data = case_for("roth_ira", birth_date="1980-06-15", roth_ira_magi=magi)
    assert calculate(data)["orders"][0]["funded"] == expected


def test_ira_deduction_is_not_contribution_permission_or_nj_basis():
    data = case_for("traditional_ira", birth_date="1980-06-15", traditional_ira_magi="86000.00")
    owner = calculate(data)["owners"][0]
    assert owner["traditional_ira"] == owner["new_nj_ira_basis"] == 7500
    assert owner["federal_ira_deduction"] == owner["new_federal_ira_basis"] == 3750
