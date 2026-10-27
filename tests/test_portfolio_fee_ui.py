"""Fee scenarios must disclose both strategy differences and outstanding obligations."""

from test_lot_ui import workbench


def test_json_fee_override_can_remove_an_imported_schedule():
    app = workbench()
    app.selectbox[0].select("Harvesting with manager fees").run()
    field = next(item for item in app.text_area if item.label.startswith("Fee schedules override"))
    field.set_value("[]")
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run(timeout=30)
    assert not app.exception
    assert not app.error
    assert app.session_state["lot_result"]["fee_summary"]["cash_assessed"] == 0
