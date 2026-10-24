"""The real editor and results expose payroll elections and their tax distinctions."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_employee_household_ui_shows_funded_and_pretax_amounts():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(
        b for b in app.button if b.label == "Load synthetic employee 401(k) household"
    ).click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert app.metric[0].value == "$201,137.00"
    assert (
        metrics["Employee 401(k) funded"],
        metrics["Pretax wage exclusion"],
        metrics["Roth employee contributions"],
    ) == ("$24,500.00", "$24,000.00", "$500.00")
