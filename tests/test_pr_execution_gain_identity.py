"""Stable source identities survive order/prefix changes and do not depend on inherited indices."""

from wealthlab.household.scenario import Scenario
from wealthlab.tax.jurisdiction_execution import evaluate
from wealthlab.tax.pr_execution_gain_example import synthetic_gain


def test_source_reordering_and_placeholder_index_cannot_redirect_actual_gain_basis_or_cash():
    baseline = evaluate(synthetic_gain())
    data = synthetic_gain().model_dump(mode="json")
    context = data["tax_plan"]["cases"][0]["pr_federal"]
    context["sources"].reverse()
    context["gain_profile"]["gains"][0]["facts"]["income_index"] = 999
    changed = evaluate(Scenario.model_validate(data))
    assert changed["rows"][-1]["net_wealth"] == baseline["rows"][-1]["net_wealth"]
    assert changed["rows"][-1]["foreign_tax_paid"] == baseline["rows"][-1]["foreign_tax_paid"]
    assert (
        changed["rows"][-1]["annual_tax"]["federal"]["income_tax"]
        == baseline["rows"][-1]["annual_tax"]["federal"]["income_tax"]
    )


def test_denied_decree_keeps_ordinary_tax_and_actual_sale_independently_runnable():
    data = synthetic_gain("ordinary").model_dump(mode="json")
    data["tax_plan"]["cases"][0]["pr_federal"]["gain_profile"]["decree"]["status"] = "denied"
    result = evaluate(Scenario.model_validate(data))
    assert result["rows"][-1]["foreign_tax_paid"] > 0
    assert result["rows"][-1]["account_balances"]["brokerage"] == 0
    assert not result["rows"][-1]["funding_failure"]
