"""The local UI offers complete source profiles and executes native selected cash flows."""

from pathlib import Path

from optimization_drilling_search_cases import case
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch


def test_starter_and_actual_native_search_are_available_in_the_local_ui():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.checkbox("drilling_starter").set_value(True).run()
    source = app.text_area("policy_search_editor").value
    assert source is not None
    profile = PolicySearch.model_validate_json(source)
    assert profile.drilling_envelope is not None
    assert profile.drilling_envelope.full_tax_optimization_supported is False
    assert [o.id for o in profile.drilling_offers] == ["well", "shares", "no_entry"]
    assert sum(a.balance for a in profile.household.accounts) == 300000
    app.text_area("policy_search_editor").set_value(case().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    result = app.session_state["policy_search_result"]
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 200000
