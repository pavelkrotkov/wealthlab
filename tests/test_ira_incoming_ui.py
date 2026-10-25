"""The real annual workbench shows received plan assets separately from spendable cash."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_direct_plan_receipt_ui_shows_separate_cash_and_basis():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("IRA withdrawals").run()
    app.selectbox[0].set_value("Direct plan rollover with withdrawals").run()
    app.button(key="FormSubmitter:ira_withdrawals-Project IRA withdrawals").click().run()
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Cash remaining before tax payments"] == "$15,000.00"
    assert metrics["Direct rollover value received inside IRAs"] == "$20,000.00"
    table = app.dataframe[0].value
    assert (table["Federal basis transferred"][0], table["NJ basis transferred"][0]) == (4000, 6000)
