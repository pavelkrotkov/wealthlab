"""Roth contributions, conversion principal and earnings have different tax consequences."""

from datetime import date

import pytest
from test_ira_withdrawals import calculate, payload

from wealthlab.retirement.roth_reconciliation import half_birthday


def roth_case(amount="40000.00"):
    data = payload()
    data["orders"] = [dict(data["orders"][2], amount=amount)]
    return data


@pytest.mark.parametrize(("year", "penalty"), [(2020, 1000), (2021, 1000), (2022, 2500)])
def test_conversion_clock_is_distinct_from_earnings_tax(year, penalty):
    """A matured conversion avoids recapture, but earnings still face early tax.

    The same $40,000 cash request consumes $10,000 regular contributions,
    $20,000 conversion principal, then $10,000 earnings. NJ uses its own ratio.
    """
    data = roth_case()
    data["owners"][0]["conversions"][0]["year"] = year
    row = calculate(data)["orders"][0]
    assert row["federal_taxable"] == 10000
    assert row["additional_tax"] == penalty
    assert row["nj_taxable"] == 16000


@pytest.mark.parametrize(
    ("when", "qualified", "penalty"), [("2026-06-14", False, 3500), ("2026-06-15", True, 0)]
)
def test_exact_age59_half_boundary(when, qualified, penalty):
    data = roth_case("50000.00")
    data["owners"][0]["birth_date"] = "1966-12-15"
    data["orders"][0]["date"] = when
    row = calculate(data)["orders"][0]
    assert row["roth_qualified"] is qualified
    assert row["additional_tax"] == penalty
    assert row["federal_taxable"] == (0 if qualified else 20000)


@pytest.mark.parametrize(("first", "taxable"), [(2021, 0), (2022, 20000)])
def test_age_alone_does_not_satisfy_first_roth_clock(first, taxable):
    """Age eliminates early tax without qualifying a Roth opened too recently.

    A 2022 first year matures in 2027, whereas a 2021 first year matures in 2026.
    The federal earnings amount remains ordinary income until both tests hold.
    """
    data = roth_case("50000.00")
    data["owners"][0].update(birth_date="1960-06-15", roth_first_year=first)
    row = calculate(data)["orders"][0]
    assert row["federal_taxable"] == taxable
    assert row["additional_tax"] == 0


def test_owner_pool_is_shared_across_roth_accounts():
    data = roth_case("20000.00")
    data["accounts"][1]["balance"] = "25000.00"
    data["accounts"].append(dict(data["accounts"][1], id="roth2"))
    data["orders"].append(dict(data["orders"][0], id="second", source="roth2"))
    rows = calculate(data)["orders"]
    assert sum(row["federal_taxable"] for row in rows) == 10000
    assert sum(row["additional_tax"] for row in rows) == 2500


def test_half_birthday_handles_end_of_month():
    assert half_birthday(date(1966, 8, 31)) == date(2026, 2, 28)
