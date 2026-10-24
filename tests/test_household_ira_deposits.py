"""Actual deposits, cash withdrawals and December tax conserve household capital."""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.ira_deposit_household_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_cash_and_accounts_reconcile_after_both_years_taxes(rows):
    assert rows[-1]["account_balances"] == dict(
        cash=Decimal(87086), retirement=Decimal(56000), roth=Decimal(11000)
    )
    assert sum(r["ira_contributions"] for r in rows) == 12000
    assert rows[-1]["net_wealth"] == Decimal(154086)


def test_ira_transfers_do_not_create_wealth_or_duplicate_spending(rows):
    taxes = sum(r["annual_tax"]["total_liability"] for r in rows if r["ira_tax_reconciled"])
    # $110k opening + $120k wages - $48k spending; deposits/conversion cancel.
    assert taxes == 27914
    assert rows[-1]["net_wealth"] == 110000 + 120000 - 48000 - taxes
    assert not any(r["funding_failure"] for r in rows)


def test_yearly_deduction_and_compensation_use_completed_income(rows):
    completed = [r for r in rows if r["ira_tax_reconciled"]]
    assert [r["annual_tax"]["federal"]["agi"] for r in completed] == [87000, 77000]
    assert [r["ira_contribution_eligibility"]["traditional_ira_magi"] for r in completed] == [
        90000,
        80000,
    ]
    assert [
        r["ira_annual_reconciliation"]["contribution_owners"][0]["federal_ira_deduction"]
        for r in completed
    ] == [3000, 3000]


def test_nj_basis_and_roth_regular_basis_carry_between_years(rows):
    owner = rows[-1]["ira_annual_reconciliation"]["owners"][0]
    assert (owner["federal_ira_basis"], owner["nj_ira_basis"]) == (0, Decimal("3777.21"))
    assert owner["roth_regular_basis"] == 1000
    assert owner["conversions"][0]["taxable_remaining"] == 10000


def test_deposits_settle_month_end_and_annual_audit_does_not_leak_forward(rows):
    first = rows[11]["ira_contribution_audit"]
    assert [r["settlement_date"] for r in first] == ["2026-01-31", "2026-07-31"]
    assert len(first) == 2
    assert len(rows[-1]["ira_contribution_audit"]) == 4
