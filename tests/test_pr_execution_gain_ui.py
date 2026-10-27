"""The country workbench executes actual linked sales and rejects unsupported credit edits."""

import json
from decimal import Decimal

from pr_execution_ui_helpers import app


def test_actual_stock_workbench_preserves_cash_and_clears_unsupported_positive_credit():
    page = app("PR stock gains")
    page.button[0].click().run()
    assert (len(page.exception), len(page.error)) == (0, 0)
    _, result = page.session_state["jurisdiction_execution_pr_gains_result"]
    assert result["rows"][-1]["net_wealth"] == Decimal("72230.15")
    edited = json.loads(page.text_area(key="jurisdiction_execution_pr_gains_editor").value)
    edited["scenario"]["tax_plan"]["cases"][0]["pr_federal"]["gain_profile"][
        "local_us_credit_treatment"
    ] = "allowed"
    page.text_area(key="jurisdiction_execution_pr_gains_editor").set_value(json.dumps(edited))
    page.button[0].click().run()
    assert "jurisdiction_execution_pr_gains_result" not in page.session_state
    assert page.error
    assert not page.exception
