"""Completed IRA taxes determine later premiums; premium cash is spent only once.

Independent CMS amounts apply to 18, 24 and 24 enrolled-person months. The
conversion creates a middle-tier lookback two years later even though the
premium year itself has only a small withdrawal and no income tax.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.medicare_household_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_cash_and_wealth_reconcile_to_taxes_spending_and_premiums(rows):
    premiums = sum(r["medicare_paid"] for r in rows)
    assert premiums == Decimal("35855.40")
    assert rows[-1]["closing_cash"] == Decimal("75076.90")
    assert rows[-1]["account_balances"] == dict(
        cash=Decimal("75076.90"), retirement=190000, roth=250000
    )
    assert rows[-1]["net_wealth"] == 750000 - 144000 - Decimal("55067.70") - premiums
    assert not any(r["funding_failure"] for r in rows)


def test_conversion_changes_two_year_lookback_not_current_income_selection(rows):
    audit = rows[-1]["medicare_audit"]
    bills = audit["bills"]
    january = [b for b in bills if b["date"].month == 1]
    assert [(b["income_year"], b["tier"]) for b in january] == [
        (2024, 2),
        (2025, 0),
        (2025, 0),
        (2026, 1),
        (2026, 1),
    ]
    generated = next(i for i in audit["income_history"] if i["year"] == 2026)
    assert (generated["agi"], generated["tax_exempt_interest"]) == (270000, 0)
    assert rows[24]["medicare_due"] == Decimal("1077.20")


def test_premium_costs_are_already_in_healthcare_and_reserve(rows):
    assert sum(r["healthcare"] for r in rows) == sum(r["medicare_paid"] for r in rows)
    assert rows[-1]["reserve_target"] == Decimal("121852.80")
    assert rows[-1]["medicare_owed"] == 0
