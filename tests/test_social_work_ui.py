"""The work-test editor runs real dated cash and clears invalid prior results."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_work_test_ui_projects_closed_year_refund_and_later_arf_cash():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("Social Security with employment").run()
    app.button(key="FormSubmitter:social_work_case-Project work-test cash").click().run()
    assert not app.exception
    assert not app.error
    rows = app.dataframe[2].value
    assert rows.iloc[16]["refund_cash"] == 491
    assert rows.iloc[76]["net_cash"] == 882
    app.text_area(key="social_work_editor").set_value("{}")
    app.button(key="FormSubmitter:social_work_case-Project work-test cash").click().run()
    assert app.error
    assert not app.metric
