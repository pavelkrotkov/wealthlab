"""Source-backed no-reduction Schedule C case uses actual W2, share cash and federal payment.

All US-taxable receipts survive locally at the same basis, so PartIII's net
exempt income and reduction are zero. A2 taxes ordinary120000 less3500 at
25251 plus100000 at15%, giving40251. Actual federal paid7419.38 leaves
PR32831.62; its separate98409.25/216500 limit does not bind that payment.
"""

from decimal import Decimal

import pytest

from wealthlab.tax.jurisdiction_execution import evaluate
from wealthlab.tax.pr_execution_mixed_gain_example import mixed_credit


@pytest.fixture(scope="module")
def result():
    return evaluate(mixed_credit())


def test_actual_pr_salary_and_premove_gain_use_positive_paid_credit_without_gross_tax_allocation(
    result,
):
    audit = result["country_assessments"]["es_income_2025"]
    final = result["rows"][-1]
    assert final["annual_tax"]["federal"]["income_tax"] == Decimal("7419.38")
    assert audit["actual_us_income_tax_paid"] == Decimal("7419.38")
    assert audit["assessment"]["regular_tax"] == 40251
    assert audit["assessment"]["regular_credit"]["allowed"] == Decimal("7419.38")
    assert audit["assessment"]["income_tax"] == Decimal("32831.62")


def test_actual_mixed_credit_has_no_future_payment_and_keeps_stock_cash_and_payroll(result):
    final = result["rows"][-1]
    assert result["reconciliation"][0]["assessments"]["es_income_2025"] == 40251
    assert final["annual_tax"]["federal"]["employee_payroll"] == 9180
    assert final["lot_audit"]["disposals"][0]["proceeds"] == 700000
    assert final["account_balances"]["brokerage"] == 0
    assert not final["funding_failure"]
