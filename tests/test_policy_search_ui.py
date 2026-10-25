"""The native form runs a bounded search and clears stale results after invalid input."""

from pathlib import Path

from optimization_cases import flat
from streamlit.testing.v1 import AppTest

from wealthlab.ui import optimization


def test_policy_form_exposes_validation_and_invalid_seed_clears_previous_result(monkeypatch):
    phases = []
    native = optimization.search

    def observed(case, *, path_progress):
        def update(phase, done, total):
            phases.append(phase)
            path_progress(phase, done, total)

        return native(case, path_progress=update)

    monkeypatch.setattr(optimization, "search", observed)
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.text_area("policy_search_editor").set_value(flat().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception
    assert not app.error
    assert "Independent validation" in phases
    assert app.session_state["policy_search_result"]["selection"] == "candidate_1"
    app.text_area("policy_search_editor").set_value("{}")
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert app.error
    assert "policy_search_result" not in app.session_state
