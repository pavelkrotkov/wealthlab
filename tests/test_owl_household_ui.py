"""Execute the public retirement UI, then reject an incompatible state-basis profile.

A prior successful result must disappear when the next submitted case fails.
The UI reports the reference policy's tax differences alongside its accounting
residual rather than calling a zero residual proof of matching tax forecasts.
"""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.skipif(date.today().year != 2026, reason="Pinned 2026 forecast comparison")
def test_reference_ui_executes_and_clears_invalid_result():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("OWL household reference").run()
    submit = "FormSubmitter:owl_reference_case-Compare retirement engines"
    data = json.loads(app.text_area(key="owl_reference_editor").value or "")
    data["synthetic"] = False
    app.text_area(key="owl_reference_editor").set_value(json.dumps(data))
    app.button(key=submit).click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$0.00"
    assert app.metric[1].value == "No"
    assert any(c.value == "Personal local inputs" for c in app.caption)
    assert app.dataframe[0].value.iloc[-1]["cumulative_tax_difference"] == Decimal("-205.59")
    reject_old_result(app, submit)


def reject_old_result(app, submit):
    data = json.loads(app.text_area(key="owl_reference_editor").value or "")
    data["nj_ira_basis"] = "0"
    app.text_area(key="owl_reference_editor").set_value(json.dumps(data))
    app.button(key=submit).click().run()
    assert not app.exception
    assert "previously-taxed NJ" in app.error[0].value
    assert not app.metric
    assert "owl_reference_result" not in app.session_state
