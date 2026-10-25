"""Household work-test input remains editable and projects actual claims, debt and tax cash."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_work_test_example_runs_and_displays_separate_government_positions():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(
        b for b in app.button if b.label == "Load synthetic Social Security with earned wages"
    ).click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    frame = cash_frame(app)
    assert frame.iloc[11]["social_security_government_receivable"] == 491
    assert frame.iloc[16]["social_security_refund_cash"] == 491
    assert_enabled(app)


def cash_frame(app):
    return next(
        f.value
        for f in app.dataframe
        if "social_security_government_receivable" in f.value and "closing_cash" not in f.value
    )


def assert_enabled(app):
    assert any(c.label == "Include earned-wage work tests" and c.value for c in app.checkbox)
