"""The native form exposes allocations and renders actual liquidated policy outcomes.

Adding a factor must update training, validation and every named robustness
case coherently. Invented history remains labelled synthetic, while a private
household cannot be overwritten by the synthetic starter transformation.
"""

import json
from pathlib import Path

import pytest
from optimization_cases import flat
from optimization_diversification_cases import case
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.diversification_example import extend
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.robustness_example import synthetic as robust
from wealthlab.optimization.validation import validate


def test_diversification_starter_and_completed_policy_results_run_in_native_workspace():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.checkbox[2].set_value(True).run()
    text = app.text_area("policy_search_editor").value
    assert isinstance(text, str)
    assert json.loads(text)["dimensions"][-1]["id"] == "diversification"
    app.text_area("policy_search_editor").set_value(case().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["policy_search_result"]
    assert result["candidates"][1]["median_real_after_tax_exit_wealth"] == 251994
    assert result["held_out"]["assessment"]["eligible"]


def test_diversification_starter_extends_all_robustness_modes_with_explicit_synthetic_history():
    starter = extend(robust())
    assert validate(starter) == 6
    for check in starter.robustness.values():
        assert [a.id for a in check.market.assets] == ["equities", "bonds"]
    history = starter.robustness["historical"].market.historical
    assert history is not None
    assert history.synthetic
    assert "zero-return bond observations" in history.source


def test_synthetic_starter_never_modifies_a_private_household():
    data = flat().model_dump(mode="json")
    data["household"]["synthetic"] = False
    with pytest.raises(ValueError, match="only extends synthetic"):
        extend(PolicySearch.model_validate(data))
