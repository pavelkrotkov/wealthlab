"""The real Household editor runs actual dated options through shared cash and tax."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_actual_household_option_form_runs_and_keeps_cash_tax_audit_visible():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(
        button for button in app.button if button.label == "Load synthetic actual option household"
    ).click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    rows = app.session_state["projection"]
    assert rows[-1]["net_wealth"] == 6500
    assert any("Actual household option cash" in item.value for item in app.subheader)
