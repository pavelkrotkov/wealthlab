"""The real Household form edits home terms and renders the actual closing evidence."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_form_edits_actual_closing_cash_and_preserves_typed_audit():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()
    next(
        b for b in app.button if b.label == "Load synthetic sourced home and lien close"
    ).click().run()
    edited = json.loads(app.text_area(key="property_editor").value or "")
    edited["holdings"][0]["sale"]["closing_costs"] = "11000"
    app.text_area(key="property_editor").set_value(json.dumps(edited))
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert (len(app.exception), len(app.error)) == (0, 0)
    last = app.session_state["projection"][-1]
    assert last["net_wealth"] == 245400
    assert last["property_audit"]["closing_events"][0]["closing_costs"] == 11000
    assert any(s.value == "Actual property, liens and closing cash" for s in app.subheader)
