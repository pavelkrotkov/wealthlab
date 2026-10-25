"""The submitted local form exposes actual gross withdrawals and net source receipts."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_workplace_cash_example_projects_through_household_form():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    button(app, "Load synthetic 401(k) cash withdrawals").click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    table = next(d.value for d in app.dataframe if "Paid gross" in d.value.columns)
    assert table.iloc[0]["Paid gross"] == 10000
    assert table.iloc[0]["Net cash received"] == 8000
    assert table.iloc[0]["Early-distribution additional tax"] == 0


def button(app, label):
    return next(b for b in app.button if b.label == label)
