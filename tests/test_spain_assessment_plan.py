"""Independent people/year assessments preserve caps, observed payments and stable identities."""

from decimal import Decimal

from spain_assessment_cases import single
from spain_cases import payment

from wealthlab.tax.spain_assessment_example import synthetic_plan
from wealthlab.tax.spain_assessment_inputs import SpainAssessmentPlan
from wealthlab.tax.spain_assessment_plan import evaluate_plan


def test_independent_people_and_years_preserve_annual_caps_and_frozen_policy():
    plan = synthetic_plan()
    before = plan.model_dump_json()
    result = evaluate_plan(plan)
    # Two supplied Toledo extensions (51439.47 each) plus Madrid (44469.73).
    assert result["total_liability_eur"] == Decimal("147348.67")
    assert (
        result["assessments"]["person_a_2026"]["liabilities_eur"]
        == result["assessments"]["person_a_2025"]["liabilities_eur"]
    )
    assert "frozen_2025" in result["assessments"]["person_a_2026"]["result"]["policy"]
    assert result["cash_execution_supported"] is False
    assert plan.model_dump_json() == before


def test_scheduled_ip_does_not_become_an_actual_paid_credit_on_repeated_evaluation():
    plan = SpainAssessmentPlan.model_validate(single())
    result = evaluate_plan(plan)
    annual = result["assessments"]["person_a_2025"]
    assert annual["liabilities_eur"]["solidarity"] == Decimal("16181.60")
    assert annual["result"]["recognized_payments_eur"]["wealth"] == 0
    assert result["obligations"][1]["fundable_eur"] == Decimal("22470.87")
    assert evaluate_plan(plan) == result


def test_actual_ip_observation_changes_assessment_and_only_remaining_schedules_are_fundable():
    data = single()
    data["annuals"][0]["case"]["payments"] = [payment("100")]
    data["obligations"][1]["amount_eur"] = "22370.87"
    data["obligations"][2]["amount_eur"] = "16081.60"
    result = evaluate_plan(SpainAssessmentPlan.model_validate(data))
    annual = result["assessments"]["person_a_2025"]
    assert annual["outstanding_eur"]["wealth"] == Decimal("22370.87")
    assert annual["liabilities_eur"]["solidarity"] == Decimal("16081.60")
    assert result["all_obligations_resolved"] is True
