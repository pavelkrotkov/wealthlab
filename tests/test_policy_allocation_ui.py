"""A native editable menu reveals the cash debit and fixed-capital comparison.

All existing starters can be composed without overwriting product IDs. The
illustration keeps all default safety targets enabled. The financial test
profile then uses its own explicit targets to exercise a complete small run.
"""

import json
from pathlib import Path

import pytest
from optimization_allocation_cases import case
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.allocation_example import extend
from wealthlab.optimization.inputs import PolicySearch


@pytest.fixture(scope="module")
def app():
    native = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    native.radio[0].set_value("Optimize").run()
    for index in range(5):
        native.checkbox[index].set_value(True).run()
    return native


def test_opening_allocation_starter_preserves_original_cash_and_existing_product_profiles(app):
    text = app.text_area("policy_search_editor").value
    assert isinstance(text, str)
    starter = PolicySearch.model_validate(json.loads(text))
    assert starter.household.accounts[0].balance == 200000
    plan = starter.household.sleeve_plan
    assert plan is not None
    assert len(plan.sleeves) == len(starter.sleeve_opportunities) == 2
    assert starter.targets.target_age == 100
    assert starter.targets.maximum_issuer_weight is not None


def test_native_search_exposes_real_cash_debits_and_constant_starting_wealth(app):
    app.text_area("policy_search_editor").set_value(case().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    result = app.session_state["policy_search_result"]
    assert result["evaluated_candidates"] == 4
    assert result["candidates"][3]["opening_allocation_audit"]["cash_debits"] == dict(cash=20000)
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 251999


def test_synthetic_opportunities_are_not_appended_to_private_scenarios():
    data = case().model_dump(mode="json")
    data["household"]["synthetic"] = False
    with pytest.raises(ValueError, match="only extends synthetic"):
        extend(PolicySearch.model_validate(data))
