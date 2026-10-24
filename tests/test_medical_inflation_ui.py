"""The real Markets editor exposes indexed bills and actual provider/cash outcomes."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_actual_medical_inflation_form_runs_the_nominal_cap_case():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("Medical bill inflation").run()
    click(app)
    assert not app.exception
    assert not app.error
    result = app.session_state["market_household_result"]["baseline"]
    assert result["aggregate"]["successes"] == 0
    assert any(m.label == "Direct HSA medical payments" for m in app.metric)
    assert any("CPI observed before the due month" in c.value for c in app.caption)


def click(app):
    next(b for b in app.button if b.label == "Project actual household paths").click().run()
