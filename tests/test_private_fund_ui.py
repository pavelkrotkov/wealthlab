"""The actual editable form must produce household outcomes and clear stale results on failure."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def workbench():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox(key="products_workbench").set_value("Conditional private fund").run()
    return app


def test_private_fund_form_runs_actual_household_cash_and_exposes_incomplete_exit():
    app = workbench()
    app.button(key="FormSubmitter:private_fund-Compare conditional private fund").click().run()
    assert not app.exception
    assert not app.error
    assert any(s.value == "Private-fund actual cash, tax and exit outcomes" for s in app.subheader)
    assert app.session_state["private_fund_result"]["exit_status"][0]["fund_complete"] is False


def test_unconfirmed_edit_clears_previous_results_in_the_same_form():
    app = workbench()
    app.button(key="FormSubmitter:private_fund-Compare conditional private fund").click().run()
    data = json.loads(app.text_area(key="private_fund_editor").value)
    data["fund"]["sleeve_plan"]["sleeves"][0]["private_fund_contract"][
        "eligibility_assumed_confirmed"
    ] = False
    app.text_area(key="private_fund_editor").set_value(json.dumps(data))
    app.button(key="FormSubmitter:private_fund-Compare conditional private fund").click().run()
    assert app.error
    assert "private_fund_result" not in app.session_state
