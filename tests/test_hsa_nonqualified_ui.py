"""A supplied nonmedical withdrawal is visible separately from qualified reimbursements."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_nonqualified_cash_hsa_example_discloses_actual_taxable_cash_and_additional_tax():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(
        b for b in app.button if b.label == "Load synthetic nonqualified HSA household"
    ).click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert (
        metrics["Qualified HSA distributions"],
        metrics["Nonqualified federal taxable cash"],
        metrics["HSA federal additional tax"],
        metrics["Conditional NJ withdrawal income"],
    ) == (
        "$3,000.00",
        "$10,000.00",
        "$2,000.00",
        "$0.00",
    )
    assert any("explicit ordinary/noninvestment assumption" in c.value for c in app.caption)
