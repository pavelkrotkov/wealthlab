"""Actual Markets UI executes complete plan-group requirements and source-tax cash."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def app():
    return AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()


def test_market_rmd_scope_uses_actual_plan_and_tax_projection():
    ui = app()
    ui.radio[0].set_value("Markets").run()
    ui.radio(key="market_workbench").set_value("Household funding").run()
    ui.selectbox(key="market_account_scope").set_value("Workplace RMDs").run()
    ui.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not ui.exception
    assert not ui.error
    table = rmd_table(ui)
    assert table.iloc[0]["Required"] == 10000
    result = ui.session_state["market_household_result"]["baseline"]
    assert result["outcomes"][0]["workplace_rmd_shortfall_total"] == 0


def rmd_table(ui):
    return next(d.value for d in ui.dataframe if "Excise case" in d.value.columns)
