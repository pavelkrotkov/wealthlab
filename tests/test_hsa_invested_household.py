"""Actual medical payments liquidate permitted HSA lots, never imaginary account cash.

The bill consumes $6,000, actual commissions $2 and custody fees $50. Selling
40.016667 shares at $120 instead of the final $110 preserves $400.17 of the
$2,000 intermediate price increase. The remaining position's final $1,000
price increase and $100 dividend complete the independent wealth bridge.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.hsa_invested_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_actual_sale_funds_bill_without_creating_household_income(rows):
    january = rows[0]
    assert january["medical_provider_paid"] == 5000
    assert january["medical_cash_paid"] == 1000
    assert january["medical_owed"] == 0
    assert january["hsa_withdrawal_cash"] == 0
    assert rows[-1]["hsa_audit"]["receipt_remaining"]["care"] == 1000


def test_separate_nj_basis_and_federal_exemption_enter_actual_return_once(rows):
    audit = rows[-1]["hsa_audit"]["investments"]
    assert audit["federal_investment_income"] == 0
    assert audit["nj_income_by_year"][2026] == dict(
        dividends=Decimal(100), interest=Decimal(0), dispositions=Decimal(2399)
    )
    assert rows[-1]["annual_tax"]["new_jersey"]["gross_income"] == 2499
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 0


def test_marked_assets_fees_and_paid_medical_bills_conserve_capital(rows):
    expected = Decimal(11100 - 6000 - 2 - 50 + 1000 + 100) + Decimal("400.17")
    assert rows[-1]["net_wealth"] == expected == Decimal("6548.17")
    assert rows[-1]["annual_tax"]["total_liability"] == 0
    assert rows[-1]["hsa_investment_fees_owed"] == 50
    assert rows[-1]["account_balances"]["hsa"] == Decimal("6598.17")
