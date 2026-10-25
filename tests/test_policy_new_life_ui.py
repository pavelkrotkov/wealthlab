"""Actual UI offers complete new-policy paths and records actual cash premiums and exit."""

from pathlib import Path

import pytest
from optimization_new_life_cases import case
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch


@pytest.fixture
def app():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    return app


def test_starter_exports_whole_quotes_and_retains_default_safety_targets(app):
    app.checkbox("new_life_starter").set_value(True).run()
    encoded = app.text_area("policy_search_editor").value
    assert encoded is not None
    profile = PolicySearch.model_validate_json(encoded)
    assert profile.targets.target_age == 100 and profile.targets.success_fraction == 0.95
    assert profile.household.life_plan is not None
    assert profile.household.life_plan.holdings == []
    assert len(profile.new_life_opportunities) == 1


def test_selected_policy_uses_actual_wallet_and_native_tax_cash_in_ui(app):
    app.text_area("policy_search_editor").set_value(case().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    result = app.session_state["policy_search_result"]
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 252099
    assert "life_premiums_paid" in str(result["selected_training"])
