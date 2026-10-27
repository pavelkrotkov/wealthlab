"""Editable complete paths are visible in the native optimizer and compose with other starters.

The synthetic example keeps the user's default horizon and concentration checks.
A separate short flat case uses explicit test targets to prove actual execution.
"""

from pathlib import Path

import pytest
from optimization_life_cases import case
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.life_example import extend


def test_native_ui_selects_complete_paths_and_keeps_capital_and_default_targets():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    for index in (3, 4, 5):
        app.checkbox[index].set_value(True).run()
    text = app.text_area("policy_search_editor").value
    assert isinstance(text, str)
    starter = PolicySearch.model_validate_json(text)
    assert len(starter.life_opportunities) == 3
    assert starter.targets.target_age == 100 and starter.targets.maximum_issuer_weight is not None
    assert len([a for a in starter.household.accounts if a.wrapper == "insurance"]) == 1
    app.text_area("policy_search_editor").set_value(case().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    result = app.session_state["policy_search_result"]
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 261999


def test_illustrative_paths_are_not_added_to_private_households():
    data = case().model_dump(mode="json")
    data["household"]["synthetic"] = False
    with pytest.raises(ValueError, match="only extends synthetic"):
        extend(PolicySearch.model_validate(data))
