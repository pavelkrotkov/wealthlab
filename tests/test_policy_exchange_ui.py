"""Editable native exchange contribution choices preserve targets and execute actual exits."""

from pathlib import Path

import pytest
from optimization_exchange_cases import case
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch


@pytest.fixture
def app():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    return app


def test_contribution_starter_exports_four_complete_profiles_and_original_source(app):
    app.checkbox("exchange_path_starter").set_value(True).run()
    encoded = app.text_area("policy_search_editor").value
    assert encoded is not None
    profile = PolicySearch.model_validate_json(encoded)
    assert profile.targets.success_fraction == 0.95 and profile.targets.target_age == 100
    assert [p.plan.contribution_quantity for p in profile.exchange_opportunities] == [
        0,
        50,
        100,
        100,
    ]
    assert all(p.plan.source_lot.quantity == 100 for p in profile.exchange_opportunities)


def test_native_search_reports_cash_and_complete_retained_source_exit(app):
    app.text_area("policy_search_editor").set_value(case().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    result = app.session_state["policy_search_result"]
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 261999
    assert "source_sale_cash" in str(result["selected_training"])
