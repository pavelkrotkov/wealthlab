"""The native optimizer exposes wrapper inputs, actual cash results and independent validation."""

import json
from pathlib import Path

from optimization_account_cases import case
from streamlit.testing.v1 import AppTest


def test_account_starter_runs_in_native_optimizer_and_exports_actual_wrapper_cash():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.checkbox[1].set_value(True).run()
    text = app.text_area("policy_search_editor").value
    assert isinstance(text, str)
    starter = json.loads(text)
    assert starter["household"]["workplace_plan"]["cash_withdrawals"]
    assert starter["household"]["hsa_plan"]["withdrawals"]
    app.text_area("policy_search_editor").set_value(case().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["policy_search_result"]
    assert result["selected_training"]["outcomes"][0]["ending_real_wealth"] == 270999
    assert result["held_out"]["assessment"]["eligible"]
