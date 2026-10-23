"""The synthetic lot workbench runs through the same engine as programmatic cases."""

from decimal import Decimal
from pathlib import Path

from streamlit.testing.v1 import AppTest


def workbench():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Tax lots").run()
    return app


def test_lot_workbench_reports_gross_scope_and_partial_sale():
    app = workbench()
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$10,995.00"
    assert "Gross lot accounting by default" in app.warning[0].value


def test_federal_wash_summary_shows_deferred_loss():
    from test_wash_sales import wash_case

    app = workbench()
    app.text_area[0].set_value(wash_case().model_dump_json())
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run()
    assert not app.exception
    assert not app.error
    assert any(item.value == "Federal wash-sale adjustments" for item in app.subheader)
    assert app.dataframe[0].value["Deferred"][0] == 250
    assert app.dataframe[0].value["Recognized"][0] == 0


def test_dated_sale_form_executes_and_displays_target():
    """The form must feed a dated snapshot into the engine and show its execution.

    A 50% weight target sells 20.025 more shares after the example manual trade.
    This catches a UI that displays the target but fails to append the decision.
    """
    from datetime import date

    app = workbench()
    app.checkbox(key="sale_enabled").check()
    app.selectbox(key="sale_mode").select("target_weight")
    app.date_input(key="sale_date").set_value(date(2026, 7, 1))
    app.text_input(key="sale_account").set_value("brokerage")
    app.text_input(key="sale_security").set_value("STOCK")
    app.text_input(key="sale_prices").set_value('{"STOCK":"100"}')
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run()
    assert not app.exception
    assert not app.error
    assert app.dataframe[0].value["Shares sold"][0] == Decimal("20.025")
    assert app.dataframe[0].value["After"][0] == 50
