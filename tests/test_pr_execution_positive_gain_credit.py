"""Independent native pre-move oracle now has actual sold shares, cash and paid-tax credit."""

from decimal import Decimal

from wealthlab.tax.jurisdiction_execution import evaluate
from wealthlab.tax.pr_execution_positive_gain_example import positive_credit


def test_real_premove_disposal_pays_7353_us_then_7646_pr_using_actual_positive_credit():
    result = evaluate(positive_credit())
    final = result["rows"][-1]
    audit = result["country_assessments"]["es_income_2025"]
    assert final["annual_tax"]["federal"]["income_tax"] == Decimal("7353.75")
    assert audit["actual_us_income_tax_paid"] == Decimal("7353.75")
    assert audit["assessment"]["income_tax"] == Decimal("7646.25")
    assert audit["assessment"]["regular_credit"]["allowed"] == Decimal("7353.75")
    assert final["lot_audit"]["disposals"][0]["proceeds"] == 700000
    assert final["account_balances"]["brokerage"] == 0
    assert not final["funding_failure"]
