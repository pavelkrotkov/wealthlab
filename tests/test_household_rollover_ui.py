"""Submitted Household forms expose funded plan-to-IRA value and actual source blocks."""

from test_workplace_rmd_ui import app, button


def test_submitted_household_direct_rollover_example_has_actual_transfer_output():
    ui = app()
    button(ui, "Load synthetic direct plan rollover").click().run()
    ui.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not ui.exception
    assert not ui.error
    metrics = {m.label: m.value for m in ui.metric}
    assert metrics["Direct plan cash rolled into IRAs"] == "$80,000.00"
    table = transfer_table(ui)
    assert (table["Funded rollover"][0], table["Unfilled request"][0]) == (80000, 0)
    assert table["Unresolved source RMD"][0] == 0


def transfer_table(ui):
    return next(d.value for d in ui.dataframe if "Funded rollover" in d.value.columns)
