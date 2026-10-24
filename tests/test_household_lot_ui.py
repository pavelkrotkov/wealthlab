"""The real form links shares to household cash, tax payments and an inspectable audit."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_actual_lot_household_ui_runs():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(
        b for b in app.button if b.label == "Load synthetic actual-lot funding household"
    ).click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert_lot_metrics(app)


def assert_lot_metrics(app):
    metrics = {m.label: m.value for m in app.metric}
    assert app.metric[0].value == "$59,831.70"
    assert metrics["Cash from lot funding sales"] == "$67,872.00"
    assert metrics["Linked accounts remaining"] == "$59,831.70"
    assert metrics["Linked trade commissions"] == "$22.00"
