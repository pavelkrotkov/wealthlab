"""Exercise actual form submission and baseline comparison without private inputs."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_form_projection():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.button(key="FormSubmitter:household-Validate and project").click().run(timeout=15)
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$224,000.00"
    assert app.metric[2].value == "$0.00"


def test_invalid_currency_json_can_be_corrected():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    field = next(item for item in app.text_input if item.label.startswith("USD per unit"))
    field.set_value("invalid")
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert app.error
    assert not app.exception
    field = next(item for item in app.text_input if item.label.startswith("USD per unit"))
    field.set_value('{"USD":1,"EUR":1.1}')
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.error
