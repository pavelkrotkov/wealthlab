"""Editable zero-opening insurance comparison preserves the uninsured protection gap."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_no_policy_new_issue_editor_runs_actual_cash_and_clears_unsupported_terms():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox("products_workbench").set_value("Whole life versus liquid saving").run()
    app.selectbox("life_comparison_opening").set_value("No policy versus new issue").run()
    key = "life_comparison_entered_uninsured"
    editor = app.text_area(key + "_editor")
    assert isinstance(editor.value, str)
    data = json.loads(editor.value)
    new = data["alternatives"]["new_issue"]["life_plan"]["holdings"][0]
    assert (
        data["alternatives"]["no_policy"]["life_plan"]["holdings"],
        new["opening_values"]["gross_death_benefit"],
    ) == ([], "0")
    app.button(key=f"FormSubmitter:{key}-Compare actual insurance alternatives").click().run()
    assert not app.exception and not app.error
    result = app.session_state[key + "_result"]
    assert result["alternatives"]["no_policy"]["outcomes"][0]["ending_protection_gap"] == 150000
    assert result["alternatives"]["new_issue"]["outcomes"][0]["closing_cash"] == 7100
    new["contract"]["federal_status"] = "unknown"
    app.text_area(key + "_editor").set_value(json.dumps(data))
    app.button(key=f"FormSubmitter:{key}-Compare actual insurance alternatives").click().run()
    assert app.error and not app.exception
    assert key + "_result" not in app.session_state
