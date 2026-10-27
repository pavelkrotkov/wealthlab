"""A refund's original recognized-tax reversal stays separate from its actual receipt FX."""

from decimal import Decimal

from spain_assessment_cases import single
from spain_cases import payment

from wealthlab.tax.spain_assessment_inputs import SpainAssessmentPlan
from wealthlab.tax.spain_assessment_plan import evaluate_plan
from wealthlab.tax.spain_example import amount


def test_original_tax_fx_and_refund_cash_fx_survive_the_multi_year_bridge():
    data = single()
    paid = payment("100")
    paid["value"] = amount("125", "2026-06-20", "USD", ".8")
    refund = payment("40", "refund", "refund", "paid")
    refund["value"] = amount("50", "2026-07-20", "USD", "1.1")
    data["annuals"][0]["case"]["payments"] = [paid, refund]
    data["obligations"] = []
    annual = evaluate_plan(SpainAssessmentPlan.model_validate(data))["assessments"]["person_a_2025"]
    result = annual["result"]
    assert result["recognized_payments_eur"]["wealth"] == Decimal("60")
    assert annual["liabilities_eur"]["solidarity"] == Decimal("16121.60")
    assert result["payments"][1]["value"]["amount"] == "50"
    assert result["payments"][1]["value"]["eur_per_unit"] == "1.1"
