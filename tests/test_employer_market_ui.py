"""The actual market form exposes employer balances and selected-path employment changes."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_employer_market_scope_runs_with_visible_work_and_liquidity():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("Employer and employment").run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    assert any(s.value == "Employer-linked value and liquidity" for s in app.subheader)
    assert any(e.label == "Market-linked employment changes" for e in app.expander)
    result = app.session_state["market_household_result"]["baseline"]
    assert result["details"][0]["employment_changes"][0]["id"] == "job_policy"
