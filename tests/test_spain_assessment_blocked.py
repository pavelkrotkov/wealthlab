"""An unresolved income source blocks dependent wealth and any instruction to fund those taxes."""

from spain_assessment_cases import single

from wealthlab.tax.spain_assessment_inputs import SpainAssessmentPlan
from wealthlab.tax.spain_assessment_plan import evaluate_plan


def test_unknown_income_never_becomes_a_fundable_annual_tax_obligation():
    data = single()
    data["annuals"][0]["case"]["incomes"][0]["spanish_base"] = "unknown"
    result = evaluate_plan(SpainAssessmentPlan.model_validate(data))
    annual = result["assessments"]["person_a_2025"]
    assert annual["liabilities_eur"] == dict(irpf=None, wealth=None, solidarity=None)
    assert result["total_liability_eur"] is None
    assert all(item["fundable_eur"] is None for item in result["obligations"])
