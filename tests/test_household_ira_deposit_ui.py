"""The real household UI exposes actual IRA deposits beside total wealth and taxes."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_deposit_example_runs_through_the_editor():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(
        b for b in app.button if b.label == "Load synthetic IRA contribution household"
    ).click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert app.metric[0].value == "$154,086.00"
    assert (metrics["Household IRA deposits funded"], metrics["Unfilled IRA deposit requests"]) == (
        "$12,000.00",
        "$0.00",
    )
