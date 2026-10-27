"""Blocked classifications and stale or excessive schedules cannot become fundable cash events."""

from decimal import Decimal

from spain_assessment_cases import single
from spain_cases import payment

from wealthlab.tax.spain_assessment_example import schedule
from wealthlab.tax.spain_assessment_inputs import SpainAssessmentPlan
from wealthlab.tax.spain_assessment_plan import evaluate_plan


def test_two_installments_cannot_each_claim_the_same_outstanding_tax():
    data = single()
    data["obligations"] = [
        schedule("first", "person_a_2025", "irpf", "12000"),
        schedule("second", "person_a_2025", "irpf", "12000"),
    ]
    result = evaluate_plan(SpainAssessmentPlan.model_validate(data))
    assert all(item["fundable_eur"] is None for item in result["obligations"])
    assert result["all_obligations_resolved"] is False
    assert result["all_assessments_resolved"] is True


def test_wealth_only_block_keeps_resolved_income_schedule_available():
    data = single()
    data["annuals"][0]["case"]["region"] = "galicia"
    data["obligations"][0]["amount_eur"] = "100"
    result = evaluate_plan(SpainAssessmentPlan.model_validate(data))
    assert result["obligations"][0]["fundable_eur"] == Decimal("100")
    assert result["obligations"][1]["fundable_eur"] is None
    assert result["total_liability_eur"] is None


def test_observed_irpf_overpayment_is_information_and_never_a_refund_entitlement():
    data = single()
    observed = payment("13000")
    observed["tax_type"] = "irpf"
    data["annuals"][0]["case"]["payments"] = [observed]
    data["obligations"] = []
    annual = evaluate_plan(SpainAssessmentPlan.model_validate(data))["assessments"]["person_a_2025"]
    assert annual["overpayment_eur"]["irpf"] == Decimal("213")
    assert annual["outstanding_eur"]["irpf"] == 0
    assert annual["refund_entitlement_inferred"] is False
