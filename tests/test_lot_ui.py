"""The synthetic lot workbench runs through the same engine as programmatic cases."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_lot_workbench_reports_gross_scope_and_partial_sale():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Tax lots").run()
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$10,995.00"
    assert "Gross lot accounting by default" in app.warning[0].value


def test_federal_wash_summary_shows_deferred_loss():
    from test_wash_sales import wash_case

    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Tax lots").run()
    app.text_area[0].set_value(wash_case().model_dump_json())
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run()
    assert not app.exception
    assert not app.error
    assert any(item.value == "Federal wash-sale adjustments" for item in app.subheader)
    assert app.dataframe[0].value["Deferred"][0] == 250
    assert app.dataframe[0].value["Recognized"][0] == 0
