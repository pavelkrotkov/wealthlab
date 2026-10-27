"""Existing household JSON controls expose conditional closure without changing actual cash."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from wealthlab.employment.compensation_exit_state import from_rows
from wealthlab.employment.compensation_termination_example import terminated


def submit(app):
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$194,980.00"
    return from_rows(app.session_state["projection"])["award"]


def remove_source_date(app):
    # Edit the same public JSON form used for ordinary compensation scenarios.
    editor = next(
        field
        for field in app.text_area
        if field.label == "Tranches, cash rights and allocation-tax assumptions (JSON)"
    )
    raw = editor.value
    assert raw is not None
    data = json.loads(raw)
    event = next(event for event in data["events"] if event["kind"] == "termination")
    event["source_date"] = None
    editor.set_value(json.dumps(data))


def test_termination_facts_edit_and_withhold_in_existing_household_form():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=90)
    app.session_state["scenario"] = terminated()
    app.run()
    assert submit(app)["contractual_exit_proven"] is True
    assert any(s.value == "Employer contractual exit evidence" for s in app.subheader)
    # Removing support changes the closure conclusion, never the actual cash.
    remove_source_date(app)
    evidence = submit(app)
    assert evidence["contractual_exit_proven"] is None
    assert evidence["termination_status"] == "unresolved"
    assert any(
        "Missing supplied termination fact: source_date" in str(d.value) for d in app.dataframe
    )
