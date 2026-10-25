"""Actual local UI exports complete source-backed profiles and executes all four cash outcomes."""

from pathlib import Path

import pytest
from optimization_qoz_cases import case
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch


@pytest.fixture
def app():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.checkbox("qoz_starter").set_value(True).run()
    assert not app.exception and not app.error
    return app


def test_qoz_starter_retains_original_capital_and_default_safety_targets(app):
    text = app.text_area("policy_search_editor").value
    assert text is not None
    profile = PolicySearch.model_validate_json(text)
    assert len(profile.qoz_offers) == 4
    assert profile.targets.target_age == 100
    assert profile.targets.success_fraction == 0.95
    assert sum(a.balance for a in profile.household.accounts) == 300000


def test_real_search_reconciles_all_four_source_backed_cash_outcomes(app):
    app.text_area("policy_search_editor").set_value(case().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    result = app.session_state["policy_search_result"]
    assert result["evaluated_candidates"] == 4
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 103753
