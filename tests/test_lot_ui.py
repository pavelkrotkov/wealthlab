"""The synthetic lot workbench runs through the same engine as programmatic cases."""

from decimal import Decimal
from pathlib import Path

from streamlit.testing.v1 import AppTest


def workbench():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Tax lots").run()
    return app


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


def test_example_switch_loads_new_json_and_clears_previous_result():
    # The installed Streamlit version includes the default text in widget
    # identity. Switching examples must replace it, and the old result must
    # disappear before a user submits the newly displayed case.
    import json

    app = workbench()
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run()
    assert app.metric
    app.selectbox[0].select("Harvesting comparison").run()
    assert json.loads(app.text_area[0].value)["compare_harvesting"] is True
    assert not app.metric
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run(timeout=30)
    assert not app.error
    assert app.dataframe[0].value["Annual tax saving"][0] == 55
