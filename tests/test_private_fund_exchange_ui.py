"""Editing a combined household must preserve its exchange plan and render both result books."""

from pathlib import Path

from private_fund_exchange_cases import combined
from streamlit.testing.v1 import AppTest


def test_mixed_household_editor_preserves_exchange_plan_and_renders_product_audits():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=120)
    app.session_state["scenario"] = combined()
    app.run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.session_state["scenario"].exchange_fund_plan is not None
    assert "exchange_fund_audit" in app.session_state["projection"][-1]
    assert "sleeve_audit" in app.session_state["projection"][-1]
    assert any("exchange_fund" in item.value for item in app.json)
