"""The native household form edits actual policy plans and renders nested audits safely."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

LABEL = "Policy ownership, values, failure settlements and reserve schedule (JSON)"


def button(app, label):
    return next(b for b in app.button if b.label == label)


def policy_field(app):
    return next(t for t in app.text_area if t.label == LABEL)


def test_household_policy_example_renders_and_rejects_incomplete_reserve_schedule():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=120)
    app.run()
    button(app, "Load synthetic whole-life household").click().run()
    button(app, "Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.session_state["projection"][-1]["net_wealth"] == 57000
    assert any(s.value == "Actual whole-life funding and protection" for s in app.subheader)
    field = policy_field(app)
    assert field.value is not None
    data = json.loads(field.value)
    data["holdings"][0]["payments_complete_through"] = "2026-04-01"
    field.set_value(json.dumps(data))
    button(app, "Validate and project").click().run()
    assert app.error
    assert "projection" not in app.session_state
