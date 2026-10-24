"""Qualified tuition leaves capital once while all wrapper elections share cash.

The synthetic opening assets are $150k. Wages add $120k, employer HSA funding
adds $2k, HSA bank interest adds $300 and 529 investments earn $6,960. Ordinary
spending consumes $60k and tuition consumes $24k; actual taxes consume $26,516.
Personal HSA/IRA/529 deposits and reimbursements are internal transfers.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.education_household_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_all_household_assets_and_paid_tuition_reconcile(rows):
    taxes = sum(r["annual_tax"]["total_liability"] for r in rows if r["ira_tax_reconciled"])
    assert taxes == 26516
    assert rows[-1]["net_wealth"] == 150000 + 120000 + 2000 + 300 + 6960 - 60000 - 24000 - taxes
    assert rows[-1]["net_wealth"] == 168744
    assert rows[-1]["closing_cash"] == 59484


def test_tuition_is_paid_once_and_is_not_household_cash_income(rows):
    assert sum(r["education"] for r in rows) == 24000
    assert sum(r["education_wrapper_paid"] for r in rows) == 24000
    assert sum(r["education_cash_fallback"] for r in rows) == 0
    assert sum(r["tax_event_cash"] for r in rows) == 45000
    assert not any(r["funding_failure"] for r in rows)


def test_basis_and_investment_value_carry_between_actual_years(rows):
    audit = rows[-1]["education_audit"]["years"]
    assert rows[-1]["account_balances"]["college"] == 24960
    assert [y["contribution_basis"]["college"] for y in audit] == [
        Decimal("18121.21"),
        Decimal("16289.65"),
    ]
    assert sum(r["education_deposits"] for r in rows) == 12000


def test_actual_qualified_payments_have_no_taxable_earnings(rows):
    groups = [y["annual_tax_groups"][0] for y in rows[-1]["education_audit"]["years"]]
    assert [g["gross_distribution"] for g in groups] == [12000, 12000]
    assert [g["federal_taxable_earnings"] for g in groups] == [0, 0]
    assert [g["federal_additional_tax"] for g in groups] == [0, 0]
    assert [g["nj_total_income"] for g in groups] == [0, 0]


def test_njbest_deduction_uses_actual_funded_deposits(rows):
    audit = rows[-1]["education_audit"]["years"]
    assert [y["njbest_funded_contributions"] for y in audit] == [6000, 6000]
    assert [y["njbest_potential_deduction"] for y in audit] == [6000, 6000]
