"""Actual salary reductions and personal/employer funding conserve assets separately.

The original $102,000 opening assets plus $120,000 salary and $500 external
employer funding are reduced only by actual taxes. All retirement/HSA deposits
and the $2,500 qualified historical reimbursement are internal transfers.
The personal $1,000 deduction is separate from $6,000 cafeteria salary reduction.
"""

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.hsa_payroll_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_hsa_cash_funding_and_household_capital_balance(rows):
    annual = rows[-1]["annual_tax"]
    assert rows[-1]["account_balances"]["cash_hsa"] == 7000
    assert rows[-1]["net_wealth"] == 102000 + 120000 + 500 - annual["total_liability"]
    assert sum(r["hsa_payroll_contributions"] for r in rows) == 6000
    assert sum(r["hsa_employer_funding"] for r in rows) == 500
    assert sum(r["hsa_payroll_unfilled"] for r in rows) == 0


def test_salary_reductions_decrease_w2_and_fica_without_second_deduction(rows):
    federal = rows[-1]["annual_tax"]["federal"]
    assert federal["agi"] == 89000
    assert federal["employee_payroll"] == 8721
    assert sum(r["hsa_personal_contributions"] for r in rows) == 1000
    annual = rows[-1]["hsa_audit"]["years"][0]
    assert annual["employer_reported_contributions"] == 6500
    assert annual["employer_funding"] == 500
    assert annual["salary_reductions"] == 6000


def test_nj_keeps_salary_reduction_in_wages_and_actual_withholding(rows):
    assert rows[-1]["annual_tax"]["new_jersey"]["gross_income"] == 96500
    # Existing pretax401k lowers NJ wages; cafeteria HSA does not in this profile.
    assert rows[0]["annual_tax"]["new_jersey"]["gross_income"] == 8500
    assert sum(r["tax_event_cash"] for r in rows) == 0
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 2500
