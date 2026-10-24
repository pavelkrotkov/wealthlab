"""The household employment example runs end to end and keeps work choices editable."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_employment_household_projects_the_same_cash_and_tax_as_the_engine():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(b for b in app.button if b.label == "Load synthetic employment household").click().run()
    assert any(c.label == "Apply dated pay changes and job loss" and c.value for c in app.checkbox)
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$167,118.50"
