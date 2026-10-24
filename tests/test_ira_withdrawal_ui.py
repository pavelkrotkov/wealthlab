"""The withdrawal screen must execute its schedule and expose cash and tax separately."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_ira_workbench_exposes_conversion_recapture_and_cash():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("IRA withdrawals").run()
    app.button(key="FormSubmitter:ira_withdrawals-Project IRA withdrawals").click().run(timeout=30)
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$35,000.00"
    assert app.dataframe[0].value["additional_tax"].sum() == 2300
    assert len(app.metric) == 2
