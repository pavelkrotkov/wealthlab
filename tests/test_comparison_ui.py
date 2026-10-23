"""The baseline survives form edits and compares a changed retirement date."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_retirement_clone_comparison():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    next(item for item in app.button if item.label.startswith("Keep this")).click().run()
    app.session_state["table_members"] = {
        "edited_rows": {0: {"retirement_date": "2028-01-01"}},
        "added_rows": [],
        "deleted_rows": [],
    }
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$344,000.00"
    assert app.metric[-1].value == "$120,000.00"
