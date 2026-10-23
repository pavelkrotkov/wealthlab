"""Matched comparisons must expose reversal on exit and preserve explicit overrides."""

from test_lot_ui import workbench


def comparison_app():
    app = workbench()
    app.selectbox[0].select("Harvesting comparison").run()
    return app


def test_synthetic_comparison_displays_holding_and_exit():
    app = comparison_app()
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run(timeout=30)
    assert not app.exception
    assert not app.error
    table = app.dataframe[0].value
    assert list(table["View"]) == ["Continue holding", "Taxable account exit"]
    assert list(table["Annual tax saving"]) == [55, 0]
    assert list(table["Marked wealth difference"]) == [0, 0]


def test_explicit_overrides_remove_comparison_and_exit():
    app = comparison_app()
    app.selectbox(key="harvest_comparison_override").select("Single run")
    app.selectbox(key="terminal_exit_override").select("No terminal exit")
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run(timeout=30)
    assert not app.exception
    assert not app.error
    assert "harvest_comparison" not in app.session_state["lot_result"]
    assert "terminal_exit" not in app.session_state["lot_result"]
    assert app.session_state["lot_result"]["harvest_decisions"]
