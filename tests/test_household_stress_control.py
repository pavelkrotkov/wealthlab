"""The household control cannot suggest an overlay in an ordinary market mode."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_stress_control_matches_the_executed_mode():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    stress = next(s for s in app.selectbox if s.label == "Household named stress")
    assert stress.disabled
    next(s for s in app.selectbox if s.label == "Household market mode").set_value("stress").run()
    assert not next(s for s in app.selectbox if s.label == "Household named stress").disabled
