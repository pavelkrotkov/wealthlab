"""The household UI makes the conditional state treatment and actual transfers visible."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_cash_hsa_household_ui_runs_and_discloses_conditional_nj():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(b for b in app.button if b.label == "Load synthetic cash HSA household").click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert app.metric[0].value == "$155,243.00"
    assert (
        metrics["Personal HSA deposits"],
        metrics["Qualified HSA reimbursements"],
        metrics["Unfilled HSA requests"],
    ) == ("$8,000.00", "$3,000.00", "$1,000.00")
    assert_conditional_caption(app)


def assert_conditional_caption(app):
    assert any("conditional NJ cash-HSA" in c.value for c in app.caption)
