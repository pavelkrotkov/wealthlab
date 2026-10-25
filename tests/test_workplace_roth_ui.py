"""The submitted Household form labels federal pro-rata cost and conditional NJ recognition."""

from test_workplace_rmd_ui import app, button


def test_roth_plan_cash_ui_shows_actual_gross_and_independent_cost_recovery():
    ui = app()
    button(ui, "Load synthetic designated Roth plan cash").click().run()
    ui.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not ui.exception
    assert not ui.error
    metrics = {m.label: m.value for m in ui.metric}
    assert metrics["Designated Roth plan gross cash"] == "$5,000.00"
    table = recovery_table(ui)
    assert table["Federal basis recovered"][0] == 4700
    assert table["Conditional NJ taxable"][0] == 500
    assert table["Additional federal tax"][0] == 30


def recovery_table(ui):
    return next(d.value for d in ui.dataframe if "Gross Roth cash" in d.value.columns)
