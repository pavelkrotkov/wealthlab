"""The actual editable product form executes paths and clears invalid envelope assumptions."""

import json
from pathlib import Path

from drilling_market_cases import price_case
from streamlit.testing.v1 import AppTest


def test_drilling_price_path_form_displays_actual_cash_and_blocks_unknown_fixed_facts():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox("products_workbench").set_value("Drilling partnerships").run()
    app.selectbox("drilling_market_method").set_value("deterministic").run()
    namespace = "drilling_market_deterministic"
    app.text_area(namespace + "_editor").set_value(price_case().model_dump_json())
    button = f"FormSubmitter:{namespace}-Compare drilling on shared price paths"
    app.button(button).click().run()
    assert not app.exception and not app.error
    result = app.session_state[namespace + "_result"]
    assert result["policies"]["drilling"]["outcomes"][0]["closing_cash"] == 140790
    data = price_case().model_dump(mode="json")
    data["binding"]["drilling"]["replace_price_observations_confirmed"] = False
    app.text_area(namespace + "_editor").set_value(json.dumps(data))
    app.button(button).click().run()
    assert app.error and not app.exception
    assert namespace + "_result" not in app.session_state
