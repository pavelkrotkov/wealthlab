"""The real Markets household workflow exposes model pricing and actual option cash/constraints."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_actual_option_market_form_runs_and_exposes_shared_batch_and_cash_audit():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("Options household").run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["market_household_result"]["baseline"]
    assert result["aggregate"]["paths"] == 1
    assert any(item.value == "Options on identical realized market paths" for item in app.subheader)
