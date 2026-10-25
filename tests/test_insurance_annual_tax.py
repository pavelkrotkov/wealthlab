"""Policy gain is ordinary income plus actual NIIT, with no pension/QBI/SE inference."""

from decimal import Decimal

from wealthlab.tax.annual import AnnualCase, evaluate, synthetic


def case(**income):
    data = synthetic().model_dump(mode="json")
    data["filing"].update(status="single", age_spouse=0)
    data["federal_income"].update(wages_primary="250000", **income)
    return AnnualCase.model_validate(data)


def test_high_wage_policy_gain_has_ordinary_tax_and_niit_once():
    base = evaluate(case())["federal"]
    result = evaluate(case(insurance_ordinary_income="10000"))["federal"]
    assert result["agi"] == 260000
    assert result["niit"] == 380
    assert result["income_tax"] - base["income_tax"] == 3580
    assert result["employee_payroll"] == base["employee_payroll"]
    assert result["insurance_ordinary_income"] == 10000


def test_magi_threshold_limits_tax_and_ordinary_pension_is_not_niit():
    data = case(insurance_ordinary_income="20000").model_dump(mode="json")
    data["federal_income"]["wages_primary"] = "190000"
    result = evaluate(AnnualCase.model_validate(data))["federal"]
    assert result["agi"] == 210000
    assert result["niit"] == 380
    pension = evaluate(case(taxable_pension="10000"))["federal"]
    assert pension["agi"] == 260000
    assert pension["niit"] == 0


def test_insurance_additional_tax_and_retirement_tax_accumulate_without_changing_agi():
    base = evaluate(case(insurance_ordinary_income="10000"))["federal"]
    result = evaluate(
        case(
            insurance_ordinary_income="10000",
            insurance_additional_tax="1000",
            retirement_additional_tax="500",
        )
    )["federal"]
    assert result["income_tax"] - base["income_tax"] == 1500
    assert result["agi"] == base["agi"]
    assert result["niit"] == base["niit"]


def test_niit_kernel_preserves_capital_netting_and_cached_return_isolation():
    baseline = evaluate(case())
    result = evaluate(case(insurance_ordinary_income="10000", long_term="-2000", interest="1000"))[
        "federal"
    ]
    assert result["niit"] == Decimal("342")  # (10,000 + 1,000 - 2,000) * 3.8%
    assert result["agi"] == 259000
    assert evaluate(case()) == baseline


def test_low_income_credits_are_not_changed_by_the_niit_only_carrier():
    insurance = case(insurance_ordinary_income="12000").model_dump(mode="json")
    insurance["federal_income"]["wages_primary"] = "10000"
    pension = case(taxable_pension="12000").model_dump(mode="json")
    pension["federal_income"]["wages_primary"] = "10000"
    left = evaluate(AnnualCase.model_validate(insurance))["federal"]
    right = evaluate(AnnualCase.model_validate(pension))["federal"]
    assert left["niit"] == 0
    assert left["income_tax"] == right["income_tax"]
    assert left["taxable_income"] == right["taxable_income"]
