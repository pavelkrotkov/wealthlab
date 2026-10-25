"""One product selector retains all workflows and restores a validated long/short editor."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_all_product_routes_preserve_the_validated_long_short_editor():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()
    app.radio[0].set_value("Products").run()
    edited = json.loads(str(app.text_area(key="long_short_editor").value))
    edited["sleeve"]["opening_equity"] = edited["reference"]["opening_equity"] = "110000"
    app.text_area(key="long_short_editor").set_value(json.dumps(edited))
    app.button(key="FormSubmitter:long_short-Compare long/short economics").click().run()
    validated = app.session_state["long_short_input"]
    app.selectbox(key="products_workbench").set_value("Conditional private fund").run()
    assert app.text_area(key="private_fund_editor")
    app.selectbox(key="products_workbench").set_value("Traditional exchange funds").run()
    assert app.text_area(key="exchange_fund_editor")
    app.selectbox(key="products_workbench").set_value("Long/short economics").run()
    assert app.text_area(key="long_short_editor").value == validated
    assert "long_short_result" in app.session_state
    assert not app.exception
    assert not app.error
