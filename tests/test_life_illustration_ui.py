"""Actual editable UI produces independent policy returns and removes invalid results."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

SUBMIT = "FormSubmitter:life_illustration-Audit supplied illustrations"


def workbench():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox(key="products_workbench").set_value("Whole-life illustrations").run()
    return app


def test_policy_form_keeps_missing_guarantees_and_retirement_obligations_visible():
    app = workbench()
    app.button(key=SUBMIT).click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["life_illustration_result"]
    assert result["illustrations"][3]["premiums_from_retirement"] == 2000
    assert result["illustrations"][4]["rows"][0]["surrender_irr"]["rate"] is None
    assert any(s.value == "Supplied policy values and dated returns" for s in app.subheader)
    app.selectbox[1].set_value("stop_funding").run()
    assert not app.exception


def test_invalid_funding_edit_clears_previous_audit():
    app = workbench()
    app.button(key=SUBMIT).click().run()
    data = json.loads(app.text_area(key="life_illustration_editor").value)
    data["illustrations"][0]["stop_funding_date"] = "2026-01-01"
    app.text_area(key="life_illustration_editor").set_value(json.dumps(data))
    app.button(key=SUBMIT).click().run()
    assert app.error
    assert "life_illustration_result" not in app.session_state
