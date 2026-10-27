"""The actual editable workbench computes and discards stale invalid results."""

import json
from pathlib import Path

from drilling_cases import short
from streamlit.testing.v1 import AppTest


def test_drilling_workbench_runs_actual_household_then_clears_invalid_result():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox(key="products_workbench").set_value("Drilling partnerships").run()
    app.text_area(key="drilling_editor").set_value(short().model_dump_json())
    submit(app)
    assert (bool(app.exception), bool(app.error)) == (False, False)
    result = app.session_state["drilling_result"]
    assert (
        result["full_tax_optimization_supported"],
        result["outcomes"]["drilling"]["closing_cash"],
    ) == (False, 140000)
    assert result["rows"]["drilling"][-1]["drilling_audit"]["months"]
    app.text_area(key="drilling_editor").set_value(json.dumps({}))
    submit(app)
    assert app.error
    assert "drilling_result" not in app.session_state


def submit(app):
    app.button(key="FormSubmitter:drilling-Compare drilling and liquid investment").click().run()
