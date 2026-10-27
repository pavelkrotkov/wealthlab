"""The editable product UI runs actual cash/tax and clears stale invalid results.

Changing the generated-price binding requires an explicit confirmation, and
only a validated comparison may replace the previously displayed calculation.
"""

import json
from pathlib import Path

from exchange_fund_cases import flat
from streamlit.testing.v1 import AppTest


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


def submit(app):
    app.button(
        key="FormSubmitter:exchange_fund-Compare exchange fund and direct sale"
    ).click().run()
