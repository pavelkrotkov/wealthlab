"""Enabling an absent Medicare plan must render an editable JSON starter."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_enabling_absent_plan_renders_unconfirmed_json():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(c for c in app.checkbox if c.label.startswith("Project Medicare bills")).check()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    starter = next(t.value for t in app.text_area if t.label.startswith("Medicare coverage,"))
    assert isinstance(starter, str)
    check_unconfirmed_json(starter)


def check_unconfirmed_json(starter):
    plan = json.loads(starter)
    assert isinstance(plan["case"]["coverage"][0]["start"], str)
    assert not plan["case"]["complete_context"]
    assert not plan["case"]["coverage"][0]["eligibility_confirmed"]
