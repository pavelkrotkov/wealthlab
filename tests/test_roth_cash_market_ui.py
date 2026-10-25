"""The submitted Markets form preserves the actual Roth contract and conditional state label."""

from test_workplace_rmd_market_ui import app


def test_market_designated_roth_example_executes_the_actual_cash_and_cost_books():
    ui = app()
    ui.radio[0].set_value("Markets").run()
    ui.radio(key="market_workbench").set_value("Household funding").run()
    ui.selectbox(key="market_account_scope").set_value("Designated Roth plan cash").run()
    ui.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not ui.exception
    assert not ui.error
    result = ui.session_state["market_household_result"]["baseline"]
    assert result["outcomes"][0]["workplace_roth_gross_cash_total"] == 5000
    metrics = {m.label: m.value for m in ui.metric}
    assert metrics["Designated Roth plan gross cash"] == "$5,000.00"
