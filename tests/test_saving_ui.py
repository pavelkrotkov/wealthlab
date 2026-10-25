"""Actual liquid saving is editable in Household and nested trades stay out of plots."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_saving_example_renders_actual_lots_and_separate_unfilled_budgets():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()
    next(b for b in app.button if b.label == "Load synthetic scheduled liquid saving").click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.session_state["projection"][-1]["net_wealth"] == 2000
    assert any(s.value == "Actual scheduled liquid saving" for s in app.subheader)
