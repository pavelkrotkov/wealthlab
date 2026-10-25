"""The real invested-HSA form shows cash and basis ingredients, then clears invalid scope."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_inside_hsa_investment_form_executes_and_clears_invalid_scope():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("HSA investments").run()
    submit = "FormSubmitter:hsa_investment-Project inside-HSA investments"
    app.button(key=submit).click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$11,645.00"
    assert app.metric[1].value == "$5,000.00"
    reject(app, submit)


def reject(app, submit):
    data = json.loads(app.text_area(key="hsa_investment_editor").value or "")
    data["ordinary_securities_no_ubti_confirmed"] = False
    app.text_area(key="hsa_investment_editor").set_value(json.dumps(data))
    app.button(key=submit).click().run()
    assert not app.exception
    assert "no UBTI" in app.error[0].value
    assert not app.metric
