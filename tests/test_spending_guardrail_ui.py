"""The real UI runs an adjustable synthetic guardrail and exposes actual spending cuts."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_guardrail_example_produces_visible_separate_lifestyle_reductions():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.checkbox(key="market_guardrail_example").check().run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    outcome = app.session_state["market_household_result"]["baseline"]["outcomes"][0]
    assert outcome["discretionary_spending_reduction"] > 0
    assert any("original uncut lifestyle" in c.value for c in app.caption)
