"""The editable product UI runs actual cash/tax and clears stale invalid results.

Changing the generated-price binding requires an explicit confirmation, and
only a validated comparison may replace the previously displayed calculation.
"""

import json
from pathlib import Path

from exchange_fund_cases import flat
from streamlit.testing.v1 import AppTest

from wealthlab.products.exchange_fund_market_example import synthetic as market_example


def test_exchange_form_runs_and_invalid_edits_clear_stale_results():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox[0].set_value("Traditional exchange funds").run()
    editor = app.text_area(key="exchange_fund_editor")
    editor.set_value(json.dumps({"scenario": flat().model_dump(mode="json")}))
    app.button(
        key="FormSubmitter:exchange_fund-Compare exchange fund and direct sale"
    ).click().run()
    assert not app.exception
    assert not app.error
    assert "exchange" in app.session_state["exchange_fund_result"]["outcomes"]
    app.text_area(key="exchange_fund_editor").set_value("{}")
    app.button(
        key="FormSubmitter:exchange_fund-Compare exchange fund and direct sale"
    ).click().run()
    assert app.error
    assert "exchange_fund_result" not in app.session_state


def test_generated_price_form_requires_explicit_replacement_confirmation():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox[0].set_value("Traditional exchange funds").run()
    scenario = flat()
    data = dict(
        scenario=scenario.model_dump(mode="json"),
        market=market_example(scenario).model_dump(mode="json"),
    )
    app.text_area(key="exchange_fund_editor").set_value(json.dumps(data))
    submit(app)
    assert app.error
    assert "Confirm replacing" in app.error[0].value
    data["replace_observations_with_market_confirmed"] = True
    app.text_area(key="exchange_fund_editor").set_value(json.dumps(data))
    submit(app)
    assert not app.error
    assert not app.exception
    assert app.session_state["exchange_fund_result"]["submitted_input"]["market"]["seed"] == 42


def submit(app):
    app.button(
        key="FormSubmitter:exchange_fund-Compare exchange fund and direct sale"
    ).click().run()
