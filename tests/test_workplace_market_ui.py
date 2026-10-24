"""Actual Markets UI includes employee-account funding and investment reconciliation."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_employee_market_scope_shows_actual_payroll_and_return_audit():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("Employee 401(k)").run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    assert any(s.value == "Employee 401(k) cash and wage reconciliation" for s in app.subheader)
    result = app.session_state["market_household_result"]["baseline"]
    assert result["details"][0]["rows"][-1]["account_balances"]["work_pretax"] > 24000
