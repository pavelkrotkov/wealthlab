"""The fixed IRA schedule is runnable and its tax timing is visible in the household UI."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_ira_household_editor_results_and_provisional_tax_scope():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=60
    ).run()
    next(b for b in app.button if b.label == "Load synthetic IRA household").click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$99,580.00"
    assert any(m.label == "IRA withdrawal cash" and m.value == "$40,000.00" for m in app.metric)
    assert any("unfinalized IRA tax" in c.value for c in app.caption)
