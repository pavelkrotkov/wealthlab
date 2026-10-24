"""Execute the HSA UI and inspect funded cash and the conditional tax consequences."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_hsa_form_uses_shared_receipts_and_reports_funded_deduction():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("HSA").run()
    app.button(key="FormSubmitter:hsa_case-Project HSA cash flows").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$4,500.00"
    assert app.metric[1].value == "$2,000.00"
    assert app.dataframe[0].value["federal_additional_tax"].sum() == 400
