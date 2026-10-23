"""Exercise submission and correction through the real annual tax form."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_annual_form_and_invalid_json_recovery():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90)
    app.run()
    app.sidebar.radio[0].set_value("Annual tax").run()
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == "$49,286.30"
    app.text_area(key="tax_filing_dependents").set_value("{")
    app.button[0].click().run()
    assert app.error
    app.text_area(key="tax_filing_dependents").set_value("[]")
    app.button[0].click().run()
    assert not app.error
    assert app.metric[0].value == "$49,286.30"
