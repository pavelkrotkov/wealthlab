"""Independent ordinary, passive and QBI controls use supplied classification instead of labels."""

from ordinary_income_cases import compute


def test_nonpassive_loss_reduces_agi_without_offsetting_investment_income_for_niit():
    result = compute(
        dict(wages_primary=300000, interest=30000, allowed_nonpassive_partnership_income=-50000)
    )
    passive = compute(dict(wages_primary=300000, interest=30000, allowed_passive_income=-50000))
    assert result["agi"] == passive["agi"] == 280000
    assert result["niit"] == 1140
    assert passive["niit"] == 0
    assert result["partnership"]["qbi_deduction"] == 0


def test_qbi_is_supplied_independently_of_nonpassive_ordinary_income():
    income = dict(wages_primary=100000, allowed_nonpassive_partnership_income=50000)
    excluded = compute(income)
    included = compute(dict(income, partnership_qbi_before_se_deduction=50000))
    assert excluded["agi"] == included["agi"] == 150000
    assert excluded["partnership"]["qbi_deduction"] == 0
    assert included["partnership"]["qbi_deduction"] == 10000
    assert excluded["employee_payroll"] == included["employee_payroll"]
    assert excluded["partnership"]["self_employment_tax"] == 0


def test_positive_partnership_income_does_not_become_investment_income_or_earned_wages():
    income = dict(wages_primary=250000, interest=30000, allowed_nonpassive_partnership_income=50000)
    result = compute(income)
    assert result["niit"] == 1140
    assert result["agi"] == 330000
    assert result["partnership"]["self_employment_tax"] == 0
    assert result["additional_medicare"] == 450
