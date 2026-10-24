"""The real household form exposes actual 529 deposits and institution payments."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_combined_education_household_form_projects():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(b for b in app.button if b.label == "Load synthetic 529 tuition household").click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert_tuition_metrics(app)


def assert_tuition_metrics(app):
    metrics = {m.label: m.value for m in app.metric}
    assert app.metric[0].value == "$168,744.00"
    assert metrics["529 deposits funded"] == "$12,000.00"
    assert metrics["Tuition paid from 529 assets"] == "$24,000.00"
    assert metrics["Tuition paid from household cash"] == "$0.00"
