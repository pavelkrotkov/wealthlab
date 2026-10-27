"""AEAT's independent Toledo IP oracle and the separate Model714/718 ordering."""

from decimal import Decimal

from spain_cases import payment

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import synthetic
from wealthlab.tax.spain_inputs import SpainCase


def test_unpaid_ip_assessment_does_not_create_solidarity_credit():
    before = evaluate(synthetic())["wealth"]["assessment"]
    data = synthetic().model_dump(mode="json")
    data["payments"] = [payment("22470.87")]
    after = evaluate(SpainCase.model_validate(data))["wealth"]["assessment"]
    assert before["solidarity_liability"] == Decimal("16181.60")
    assert after["solidarity_liability"] == 0
    assert before["wealth"] == after["wealth"]
    assert after["wealth_actually_paid"] == Decimal("22470.87")


def test_madrid_bonus_uses_capped_solidarity_before_actual_paid_ip_credit():
    before = evaluate(synthetic("madrid"))["wealth"]["assessment"]
    data = synthetic("madrid").model_dump(mode="json")
    data["payments"] = [payment("16181.60")]
    after = evaluate(SpainCase.model_validate(data))["wealth"]["assessment"]
    assert before["madrid_bonus"] == Decimal("6289.27")
    assert before["wealth_liability"] == Decimal("16181.60")
    assert before["solidarity_liability"] == Decimal("16181.60")
    assert after["solidarity_liability"] == 0
