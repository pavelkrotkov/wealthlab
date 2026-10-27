"""The actual product form renders cash/tax results and discards stale invalid output."""

from pathlib import Path

from qoz_cases import flat
from streamlit.testing.v1 import AppTest


def test_qoz_form_runs_real_household_and_preserves_other_product_routes():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox(key="products_workbench").set_value("Opportunity-zone funds").run()
    app.text_area(key="qoz_editor").set_value(flat().model_dump_json())
    button = "FormSubmitter:qoz-Compare QOZ tax and liquidity"
    app.button(key=button).click().run()
    assert not app.exception
    assert not app.error
    assert "denied" in app.session_state["qoz_result"]["outcomes"]
    assert app.session_state["qoz_result"]["rows"]["allowed"][-1]["qoz_settlement_cash"] == 80000
    app.text_area(key="qoz_editor").set_value("{}")
    app.button(key=button).click().run()
    assert app.error
    assert "qoz_result" not in app.session_state
