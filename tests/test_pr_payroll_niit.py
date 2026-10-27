"""Territory exclusions never erase payroll or NIIT on independently taxable US income."""

from decimal import Decimal

from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.pr_examples import synthetic
from wealthlab.tax.pr_incentive_examples import legacy_dividends
from wealthlab.tax.pr_incentives import evaluate
from wealthlab.tax.pr_inputs import income


def dividend_case(amount, wages=0):
    comparison = legacy_dividends()
    dividend = comparison.annual.income[0].model_copy(
        update={
            "federal_amount": Decimal(amount),
            "pr_amount": Decimal(amount),
            "qualified_dividends": Decimal(amount),
        }
    )
    rows = [dividend]
    if wages:
        rows.append(
            synthetic()
            .income[0]
            .model_copy(update={"federal_amount": Decimal(wages), "pr_amount": Decimal(wages)})
        )
    baseline = comparison.annual.baseline.model_copy(
        update={
            "federal_income": income(rows),
            "nj_income": NJIncome(wages=Decimal(wages), dividends=Decimal(amount)),
        }
    )
    annual = comparison.annual.model_copy(update={"baseline": baseline, "income": rows})
    return comparison.model_copy(update={"annual": annual})


def test_raw_additional_medicare_remains_in_the_incentive_payroll_audit():
    # 2025 employee FICA: 176,100 x6.2% +250,000 x1.45% +50,000 x0.9%.
    # Section933 income-tax exclusion does not remove the original wage base.
    result = evaluate(dividend_case(100000, 250000))
    candidate = result["incentive"]
    assert result["baseline"]["federal"]["additional_medicare"] == 450
    assert candidate["federal"]["additional_medicare"] == 450
    assert candidate["employee_payroll"] == Decimal("14993.20")


def test_local_legacy_exemption_does_not_exempt_us_source_dividends_from_niit():
    # Taxable US gain/dividend income484,250: (484,250-48,350)x15%=65,385.
    # NIIT is min(500k investment,500k-200k MAGI)x3.8%=11,400.
    result = evaluate(dividend_case(500000))
    candidate = result["incentive"]
    assert candidate["federal"]["niit"] == 11400
    assert candidate["federal"]["income_tax"] == 76785
    assert candidate["puerto_rico"]["income_tax"] == 0
    assert result["ordinary"] is None
    assert "NIIT" in " ".join(result["reasons"])
