"""The actual Markets form produces visible funding outcomes and ledger details."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_actual_household_market_form_runs_a_real_synthetic_path():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    next(b for b in app.button if b.label == "Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].label == "Funded paths / supplied horizon"
    assert any("Shared realized batch" in c.value for c in app.caption)
