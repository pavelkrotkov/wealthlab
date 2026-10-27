"""Native UI composes independent starters without relaxing safety requirements.

Imported policy JSON uses the same engine as financial checks. The public
starter retains age and concentration constraints even though supplied product
inventories cannot satisfy them; a deliberately bounded test profile supplies
its own targets. Audit export exposes the executed exchange termination state.
"""

import json
from pathlib import Path

import pytest
from optimization_product_cases import case
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example import extend


@pytest.fixture(scope="module")
def app():
    native = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    native.radio[0].set_value("Optimize").run()
    for index in range(4):
        native.checkbox[index].set_value(True).run()
    return native


def test_product_starter_composes_and_preserves_default_constraints(app):
    text = app.text_area("policy_search_editor").value
    assert isinstance(text, str)
    starter = PolicySearch.model_validate(json.loads(text))
    assert starter.household.life_plan and starter.household.sleeve_plan
    assert starter.household.exchange_fund_plan and starter.household.hsa_plan
    assert starter.targets.target_age == 100
    assert starter.targets.maximum_issuer_weight is not None


def test_product_history_retains_synthetic_provenance_and_all_factor_dimensions(app):
    text = app.text_area("policy_search_editor").value
    assert isinstance(text, str)
    starter = PolicySearch.model_validate(json.loads(text))
    assert len(starter.training.assets) == 3
    history = starter.robustness["historical"].market.historical
    assert history is not None
    assert "synthetic zero-return exchange" in history.source


def test_example_cannot_append_synthetic_assets_to_private_household():
    profile = case()
    data = profile.model_dump(mode="json")
    data["household"]["synthetic"] = False
    with pytest.raises(ValueError, match="only extends synthetic"):
        extend(PolicySearch.model_validate(data))
