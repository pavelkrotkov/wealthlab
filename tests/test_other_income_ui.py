"""The real annual form exposes and submits the new distinct typed classification."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from wealthlab.tax.annual import synthetic
from wealthlab.tax.facts import FederalIncome


def test_annual_form_includes_other_income_without_treating_it_as_wages():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=90)
    case = synthetic().model_copy(
        update=dict(
            federal_income=FederalIncome(
                wages_primary=200000,
                ordinary_noninvestment_income=10000,
            )
        )
    )
    app.session_state["annual_case"] = case
    app.run().sidebar.radio[0].set_value("Annual tax").run()
    app.button[0].click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["annual_result"]["federal"]
    assert (result["agi"], result["ordinary_noninvestment_income"]) == (210000, 10000)
    assert "carrier" in result["ordinary_noninvestment_adapter"]
