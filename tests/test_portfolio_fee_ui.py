"""Fee scenarios must disclose both strategy differences and outstanding obligations."""

from decimal import Decimal as D

from test_lot_ui import workbench


def test_manager_fee_example_flows_through_the_comparison_ui():
    app = workbench()
    app.selectbox[0].select("Harvesting with manager fees").run()
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run(timeout=30)
    assert not app.exception
    assert not app.error
    comparison = app.dataframe[0].value
    assert comparison["Extra cash fees"][0] == D("5.01")
    assert comparison["Tax-adjusted difference"][0] == D("49.99")
    assert any("Cash fees assessed: USD 5.01" in item.value for item in app.caption)


def test_json_fee_override_can_remove_an_imported_schedule():
    app = workbench()
    app.selectbox[0].select("Harvesting with manager fees").run()
    field = next(item for item in app.text_area if item.label.startswith("Fee schedules override"))
    field.set_value("[]")
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run(timeout=30)
    assert not app.exception
    assert not app.error
    assert app.session_state["lot_result"]["fee_summary"]["cash_assessed"] == 0
