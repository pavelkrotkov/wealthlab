"""Cash HSA assets and taxes reconcile with the household's IRA deposits.

Opening HSA cash is $10k; $8k personal deposits, $2k employer funding and
$300 bank interest less $3k historical reimbursements leave $17,300. Personal
transfers and reimbursements cancel in household wealth; employer funds and
interest are external additions. The old medical bill is already reflected
in opening history and is not charged again. NJ wages and interest below
are the explicitly selected conditional bank treatment, not a legal finding.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.hsa_household_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_hsa_and_household_capital_conserve_transfers(rows):
    taxes = sum(r["annual_tax"]["total_liability"] for r in rows if r["ira_tax_reconciled"])
    assert taxes == 27057
    assert rows[-1]["net_wealth"] == 120000 + 120000 + 2000 + 300 - 60000 - taxes
    assert rows[-1]["net_wealth"] == 155243


def test_hsa_ending_cash_book_matches_actual_deposits_and_claims(rows):
    assert rows[-1]["account_balances"]["cash_hsa"] == 10000 + 8000 + 2000 + 300 - 3000
    assert rows[-1]["closing_cash"] == 70943
    assert sum(r["hsa_personal_contributions"] for r in rows) == 8000


def test_shared_historical_receipt_cannot_be_used_again_next_year(rows):
    annual = rows[-1]["hsa_audit"]["years"]
    assert [r["remaining_receipts"]["past_medical"] for r in annual] == [1000, 0]
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 3000
    assert sum(r["hsa_unfilled_requests"] for r in rows) == 1000


def test_hsa_deduction_reduces_agi_but_personal_deposits_keep_full_payroll(rows):
    completed = [r for r in rows if r["ira_tax_reconciled"]]
    assert [r["annual_tax"]["federal"]["agi"] for r in completed] == [83000, 73000]
    assert [r["annual_tax"]["federal"]["employee_payroll"] for r in completed] == [4590, 4590]
    assert [r["ira_contribution_eligibility"]["traditional_ira_magi"] for r in completed] == [
        86000,
        76000,
    ]


def test_conditional_nj_employer_and_bank_income_stays_separate(rows):
    completed = [r for r in rows if r["ira_tax_reconciled"]]
    assert [r["annual_tax"]["new_jersey"]["gross_income"] for r in completed] == [
        Decimal("90276.21"),
        Decimal("79801"),
    ]
    assert rows[-1]["hsa_audit"]["nj_treatment"] == "taxable_bank_interest_assumption"
    assert sum(r["hsa_employer_funding"] for r in rows) == 2000
