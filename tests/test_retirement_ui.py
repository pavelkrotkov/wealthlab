"""Run the synthetic retirement allocation through its actual user-facing form."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_retirement_form_exposes_funding_failure_and_distinct_basis():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.button(key="FormSubmitter:retirement_contributions-Allocate contributions").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$0.00"
    assert app.dataframe[0].value["unfunded"].sum() == 4350
    assert app.dataframe[1].value["new_nj_ira_basis"][0] == 4250
    assert app.dataframe[1].value["federal_ira_deduction"][0] == 0
