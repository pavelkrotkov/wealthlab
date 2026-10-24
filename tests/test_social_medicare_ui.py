"""The household UI exposes gross benefits, net receipts and withheld premiums separately."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_withholding_household_ui_reconciles_gross_net_and_premiums():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(
        b
        for b in app.button
        if b.label == "Load synthetic Social Security with Medicare withholding"
    ).click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert app.metric[0].value == "$212,354.20"
    assert (
        metrics["Gross Social Security credited"],
        metrics["Social Security cash received"],
        metrics["Medicare withheld from benefits"],
    ) == ("$152,243.00", "$138,040.00", "$14,203.00")
