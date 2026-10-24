"""Vesting moves existing value; grants/returns and actual distributions remain separate."""

from decimal import Decimal

import pytest

from wealthlab.employment.compensation_example import synthetic
from wealthlab.household.projection import project


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


@pytest.mark.parametrize(
    ("month", "vested", "unvested", "cash"),
    [
        (0, 20000, 90000, 0),
        (2, 22000, 99000, 0),
        (4, 22000, 79000, 20000),
        (5, 42000, 59000, 0),
        (11, 101000, 0, 0),
        (13, 91000, 0, 10000),
    ],
)
def test_event_values_and_actual_cash_reconcile(rows, month, vested, unvested, cash):
    row = rows[month]
    assert row["employer_vested"] == vested
    assert row["employer_unvested_contingent"] == unvested
    assert row["employer_distribution_cash"] == row["tax_event_cash"] == cash
    assert row["account_balances"]["employer_fund"] == vested


def test_optional_locked_request_is_not_a_spending_obligation(rows):
    assert rows[11]["employer_distribution_not_paid"] == 20000
    assert rows[11]["employer_locked_vested"] == 101000
    assert rows[11]["funding_failure"] is False
    assert rows[12]["employer_redeemable"] == 101000


def test_non_cash_allocation_and_complete_household_reconciliation(rows):
    assert rows[3]["tax_event_cash"] == 0
    annual = rows[11]["annual_tax"]
    assert annual["federal"]["agi"] == 110000
    assert annual["federal"]["employee_payroll"] == 6885
    assert annual["total_liability"] == 19020
    assert rows[-1]["closing_cash"] == 104980
    assert rows[-1]["net_wealth"] == 295980
    # Opening marked+contingent300k + grant10k + net growth11k + wages90k
    # less spending96k and tax19020. No remaining contingent value is hidden.
    assert rows[-1]["net_wealth"] == Decimal(300000 + 10000 + 11000 + 90000 - 96000 - 19020)
