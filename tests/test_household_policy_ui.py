"""A visible synthetic concentration policy runs the actual monthly ledger."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_actual_market_policy_controls_and_decisions_are_visible():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_policy_example").set_value("Concentration target").run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    assert any(s.value == "Actual sale and harvesting decisions" for s in app.subheader)
    audit = app.session_state["market_household_result"]["baseline"]["details"][0]["rows"][-1][
        "lot_audit"
    ]
    assert audit["sale_decisions"][0]["sold_units"] > 0
