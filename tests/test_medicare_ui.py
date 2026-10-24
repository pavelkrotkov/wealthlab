"""Execute the Medicare workbench and inspect funded costs and the income lookback."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_medicare_workbench_reports_cash_and_dated_arrears():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("Medicare").run()
    app.button(key="FormSubmitter:medicare_case-Project Medicare costs").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$2,071.00"
    assert app.metric[1].value == "$0.00"
    assert app.metric[2].value == "$7,299.40"
    assert app.dataframe[0].value["unfunded_at_due"].sum() > 0
