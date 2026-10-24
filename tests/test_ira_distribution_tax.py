"""Additional retirement tax is a liability input, never an extra income amount."""

from decimal import Decimal

from wealthlab.retirement.distribution_example import synthetic
from wealthlab.retirement.distributions import run
from wealthlab.tax.annual import evaluate


def test_additional_tax_enters_form1040_once_without_changing_agi_or_payroll():
    case = synthetic().annual_tax_case
    assert case is not None
    original = evaluate(case)["federal"]
    income = case.federal_income.model_copy(update=dict(retirement_additional_tax=Decimal(1000)))
    revised = evaluate(case.model_copy(update=dict(federal_income=income)))["federal"]
    assert revised["agi"] == original["agi"]
    assert revised["employee_payroll"] == original["employee_payroll"]
    assert revised["income_tax"] - original["income_tax"] == 1000


def test_distribution_tax_comparison_uses_taxable_amounts_and_keeps_cash_gross():
    result = run(synthetic())
    annual = result["annual_tax"]
    assert annual["without_distributions"]["federal"]["agi"] == 100000
    assert annual["with_distributions"]["federal"]["agi"] == 124000
    assert sum(row["additional_tax"] for row in result["orders"]) == 2300
    assert annual["additional_liability"] > 2300
    assert result["cash"] == 35000
