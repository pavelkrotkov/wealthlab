"""Published monthly contribution limits include Medicare and separate catch-ups."""

import pytest
from test_hsa_cash import calculate, payload


def single_case(year=2025):
    data = payload()
    data.update(
        year=year,
        married=False,
        contributions=[],
        withdrawals=[],
        interest=[],
        medical_receipts=[],
        opening_cash="10000.00",
    )
    data["owners"] = [data["owners"][1]]
    data["owners"][0]["birth_date"] = f"{year - 65}-07-01"
    data["accounts"] = [data["accounts"][1]]
    for month in data["owners"][0]["months"]:
        month["coverage"] = "self"
    return data


@pytest.mark.parametrize(("year", "expected"), [(2025, 2650), (2026, 2700)])
def test_irs_midyear_medicare_example(year, expected):
    # Half a year's self-only base and half an age-55 catch-up, not a full catch-up.
    data = single_case(year)
    assert calculate(data)["contribution_limits"]["spouse"] == expected


def test_monthly_family_pool_reallocates_after_spouse_medicare():
    limits = calculate(payload())["contribution_limits"]
    assert limits == {"person": 7562.50, "spouse": 2687.50}
    assert sum(limits.values()) == 10250  # $8,750 family base plus $1,500 eligible catch-ups.


@pytest.mark.parametrize("reason", ["medicare", "disqualifying_coverage", "claimable_dependent"])
def test_ineligible_months_supply_no_contribution_room(reason):
    data = single_case()
    for month in data["owners"][0]["months"]:
        month[reason] = True
    assert calculate(data)["contribution_limits"]["spouse"] == 0


def test_contribution_after_coverage_ends_can_use_earned_annual_room():
    data = single_case()
    data["contributions"] = [
        dict(
            id="late",
            provenance="assumption",
            date="2025-12-15",
            destination="spouse_hsa",
            source="personal_cash",
            amount="5000.00",
        )
    ]
    result = calculate(data)
    assert result["orders"][0]["funded"] == 2650
    assert result["personal_federal_deduction"] == 2650
