"""Later premium payments cure bills without erasing their original cash failures.

March cash pays three monthly bills, including two already missed. Those
arrears are a liability payment, not a tripling of recurring healthcare needs.
The annual total of original cash gaps can exceed the final unpaid balance.
"""

from datetime import date
from decimal import Decimal

import pytest

from tests.medicare_household_cases import cash_stress
from wealthlab.household.projection import project


@pytest.fixture(scope="module")
def rows():
    return project(cash_stress())


def test_unpaid_premiums_reduce_wealth_and_never_borrow_from_an_ira(rows):
    assert rows[0]["medicare_owed"] == Decimal("202.90")
    assert rows[0]["closing_cash"] == 0
    assert rows[0]["net_wealth"] == Decimal("499797.10")
    assert rows[-1]["medicare_owed"] == Decimal("2652.20")
    assert rows[-1]["net_wealth"] == Decimal("497347.80")


def test_arrears_payment_does_not_inflate_current_reserve(rows):
    march = rows[2]
    assert march["healthcare"] == Decimal("608.70")
    assert march["medicare_arrears_paid"] == Decimal("405.80")
    assert march["medicare_unfunded"] == 0
    assert march["reserve_target"] == Decimal("4869.60")
    assert rows[0]["funding_failure"] and rows[1]["funding_failure"]


def test_bill_audit_preserves_due_failure_and_actual_payment_month(rows):
    audit = rows[-1]["medicare_audit"]
    first = audit["bills"][0]
    assert first["unfunded"] == 0
    assert first["unfunded_at_due"] == Decimal("202.90")
    payment = next(p for p in audit["payments"] if p["due"] == first["id"])
    assert payment["date"] == date(2026, 3, 1)
    assert sum(r["medicare_unfunded"] for r in rows) == Decimal("3058.00")
