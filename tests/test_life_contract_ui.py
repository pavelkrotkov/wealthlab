"""Contract tax/unknowns and invalid-input recovery work through the actual UI."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

SUBMIT = "FormSubmitter:life_contract-Audit policy cash and taxes"


def test_lapse_tax_then_unknown_treatment_and_invalid_edit_clear_results():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=120)
    app.run().radio[0].set_value("Products").run()
    app.selectbox(key="products_workbench").set_value("Whole-life contract cash and taxes").run()
    app.button(key=SUBMIT).click().run()
    clean(app)
    assert app.metric[0].value == "$0.00"
    result = app.session_state["life_contract_result"]
    assert result["annual"][0]["tax_change"] > 0
    edited = app.text_area(key="life_contract_editor").value
    assert edited is not None
    data = json.loads(edited)
    data["contract"]["federal_status"] = "unknown"
    app.text_area(key="life_contract_editor").set_value(json.dumps(data))
    app.button(key=SUBMIT).click().run()
    assert app.session_state["life_contract_result"]["annual"][0]["tax_change"] is None
    data["contract"]["events"][-1]["amount"] = "1"
    app.text_area(key="life_contract_editor").set_value(json.dumps(data))
    app.button(key=SUBMIT).click().run()
    assert app.error
    assert "life_contract_result" not in app.session_state


def clean(app):
    assert not app.exception
    assert not app.error
