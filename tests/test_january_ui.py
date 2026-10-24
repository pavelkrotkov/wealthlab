"""The real UI distinguishes corrected returns from actual delayed refund cash."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_january_household_example_and_dated_return_audit_are_visible():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(
        b for b in app.button if b.label == "Load synthetic January wash reconciliation"
    ).click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$280,713.00"
    assert any(
        s.value == "January wash and original-year return reconciliation" for s in app.subheader
    )
    assert any("Historical payments stay unchanged" in c.value for c in app.caption)
