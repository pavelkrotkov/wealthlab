"""A real higher pre-move gain cannot turn US NIIT into an unverified PR credit."""

import pytest

from wealthlab.household.scenario import Scenario
from wealthlab.tax.jurisdiction_execution import evaluate
from wealthlab.tax.pr_execution_positive_gain_example import positive_credit


def test_material_niit_does_not_enter_the_local_paid_us_tax_credit_by_default():
    data = positive_credit().model_dump(mode="json")
    asset = data["tax_plan"]["cases"][0]["pr_federal"]["gain_profile"]["gains"][0]["facts"]
    asset.update(federal_move_fmv="400000", pr_move_fmv="400000")
    with pytest.raises(ValueError, match="NIIT"):
        evaluate(Scenario.model_validate(data))


def test_denied_local_credit_keeps_actual_niit_and_stock_cash_once():
    data = positive_credit().model_dump(mode="json")
    profile = data["tax_plan"]["cases"][0]["pr_federal"]["gain_profile"]
    profile["local_us_credit_treatment"] = "denied"
    profile["gains"][0]["facts"].update(federal_move_fmv="400000", pr_move_fmv="400000")
    result = evaluate(Scenario.model_validate(data))
    final = result["rows"][-1]
    audit = result["country_assessments"]["es_income_2025"]
    assert final["annual_tax"]["federal"]["niit"] == 3800
    assert audit["assessment"]["regular_credit"]["allowed"] == 0
    assert final["lot_audit"]["disposals"][0]["proceeds"] == 700000
    assert final["account_balances"]["brokerage"] == 0
