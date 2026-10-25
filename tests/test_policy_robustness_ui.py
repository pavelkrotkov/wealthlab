"""The native form exposes named checks and renders a failed required exit validation."""

import json
from pathlib import Path

from optimization_robustness_cases import case
from streamlit.testing.v1 import AppTest


def test_robustness_starter_and_failed_required_check_render_in_native_workspace():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.checkbox[0].set_value(True).run()
    text = app.text_area("policy_search_editor").value
    assert isinstance(text, str)
    starter = json.loads(text)
    assert len(starter["robustness"]) == 6
    data = case().model_dump(mode="json")
    data["robustness"] = dict(exit_lock=data["robustness"]["exit_lock"])
    app.text_area("policy_search_editor").set_value(json.dumps(data))
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception
    assert not app.error
    assert not app.session_state["policy_search_result"]["configured_validation_passed"]
    assert len(app.dataframe) == 2
