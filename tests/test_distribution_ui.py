"""The synthetic distribution example exposes cash timing and partial dividend qualification."""

from test_lot_ui import workbench


def test_distribution_example_reports_entitled_cash_and_qualified_subset():
    app = workbench()
    app.selectbox[0].select("Distributions and dividend holding").run()
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run(timeout=30)
    assert not app.exception
    assert not app.error
    table = app.dataframe[0].value
    assert table["amount"][0] == 100
    assert table["qualified"][0] == 60
    assert table["paid"][0]
    assert app.metric[0].value == "$1,100.00"
    assert any("Earned but unpaid: USD 0.00" in item.value for item in app.caption)
