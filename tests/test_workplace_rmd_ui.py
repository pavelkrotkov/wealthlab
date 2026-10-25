"""Submitted Household and Markets forms show per-plan RMD requirements and actual cash."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def app():
    return AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()


def test_household_rmd_example_displays_distinct_plan_requirements():
    ui = app()
    button(ui, "Load synthetic separate-plan RMDs").click().run()
    ui.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not ui.exception
    assert not ui.error
    table = rmd_table(ui)
    assert table.iloc[0]["Required"] == 10000
    assert table.iloc[0]["Distributed"] == 15000
    assert table.iloc[1]["Distributed"] == 10000


def button(ui, label):
    return next(b for b in ui.button if b.label == label)


def rmd_table(ui):
    return next(d.value for d in ui.dataframe if "Excise case" in d.value.columns)
