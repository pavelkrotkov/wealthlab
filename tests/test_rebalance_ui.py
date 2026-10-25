"""The actual form runs both policies and exposes executed weights and costs."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_rebalance_form_runs_a_matched_hold_comparison():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("Taxable rebalancing").run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    bundle = app.session_state["market_household_result"]
    assert bundle["comparison"]["result"]["batch_id"] == bundle["baseline"]["batch_id"]
    assert any(s.value == "Actual taxable rebalancing" for s in app.subheader)
