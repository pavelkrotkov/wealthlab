"""The native form preserves default safety targets and shows actual contract exit evidence."""

from pathlib import Path

import pytest
from optimization_contract_cases import case
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch


@pytest.fixture
def app():
    native = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    native.radio[0].set_value("Optimize").run()
    selected = next(
        c for c in native.checkbox if c.label == "Add synthetic options and employer contract exits"
    )
    selected.set_value(True).run()
    return native


def test_contract_starter_preserves_default_targets_and_supplied_plans(app):
    encoded = app.text_area("policy_search_editor").value
    assert encoded is not None
    offered = PolicySearch.model_validate_json(encoded)
    assert offered.targets.success_fraction == 0.95
    assert offered.targets.target_age == 100
    assert offered.household.option_plan and offered.household.compensation_plan


def test_search_exposes_actual_cash_and_conditional_contractual_exit_evidence(app):
    app.text_area("policy_search_editor").set_value(case().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["policy_search_result"]
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 282338
    assert "contractual_exit_proven" in str(result["selected_training"])
