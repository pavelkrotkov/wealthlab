"""The household form can opt into taxes and show reconciled cash-flow results."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_tax_toggle_projects_and_remains_editable():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(
        item for item in app.checkbox if item.label == "Calculate federal and New Jersey taxes"
    ).check()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$200,932.50"
    assert any(item.value == "Taxes on recognized income" for item in app.subheader)
