"""Submitted Markets form retains actual transfer output and source-plan accounting."""

from test_workplace_rmd_market_ui import app


def test_market_rollover_scope_executes_the_actual_household_ledger():
    ui = app()
    ui.radio[0].set_value("Markets").run()
    ui.radio(key="market_workbench").set_value("Household funding").run()
    ui.selectbox(key="market_account_scope").set_value("Direct plan rollovers").run()
    ui.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not ui.exception
    assert not ui.error
    result = ui.session_state["market_household_result"]["baseline"]
    assert result["outcomes"][0]["workplace_rollover_funded_total"] == 80000
    metrics = {m.label: m.value for m in ui.metric}
    assert metrics["Direct plan cash rolled into IRAs"] == "$80,000.00"
