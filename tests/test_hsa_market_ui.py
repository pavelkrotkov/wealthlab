"""Real Markets form runs invested HSA medical funding and displays asset/cash distinction."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_invested_hsa_market_form_runs_actual_shares_and_medical_cash():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("Invested HSA").run()
    next(b for b in app.button if b.label == "Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["market_household_result"]["baseline"]
    assert result["aggregate"]["successes"] == 1
    assert any(m.label == "Invested HSA net assets" for m in app.metric)
    assert any(m.label == "Direct HSA medical payments" for m in app.metric)
