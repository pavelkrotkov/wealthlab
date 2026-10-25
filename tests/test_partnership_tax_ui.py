"""The existing real annual editor exposes all independently supplied partnership inputs."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from wealthlab.tax.annual import synthetic
from wealthlab.tax.facts import FederalIncome


def test_annual_form_submits_independent_nonpassive_and_qbi_inputs():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=90)
    case = synthetic().model_copy(
        update=dict(
            federal_income=FederalIncome(
                wages_primary=100000,
                allowed_nonpassive_partnership_income=50000,
                partnership_qbi_before_se_deduction=50000,
            )
        )
    )
    app.session_state["annual_case"] = case
    app.run().sidebar.radio[0].set_value("Annual tax").run()
    app.button[0].click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["annual_result"]["federal"]
    assert result["agi"] == 150000
    assert result["partnership"]["qbi_deduction"] == 10000
    assert "numerical QBI offset" in result["partnership"]["qbi_adapter"]
