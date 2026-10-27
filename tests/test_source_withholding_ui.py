"""The editable local UI exposes gross pension, net cash and payer tax separately."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_source_withholding_example_projects_and_displays_cash_reconciliation():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    labelled(app.button, "Load synthetic pension with source withholding").click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    table = receipt_table(app)
    assert table.iloc[0]["Gross cash"] == 10000
    assert table.iloc[0]["Net cash received"] == 8000
    assert table.iloc[0]["Federal tax withheld"] == 2000
    assert table.iloc[0]["Foreign tax withheld"] == 0
    assert table.iloc[0]["Foreign payment identity"] is None


def labelled(items, label):
    return next(item for item in items if item.label == label)


def receipt_table(app):
    return next(d.value for d in app.dataframe if "Gross cash" in d.value.columns)
