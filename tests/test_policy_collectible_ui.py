"""The visible original gold starter executes the same complete native search.

A preset preserves the household safety targets. Editing its finite inputs in
the real form then runs the independent flat-price cash case without an upload
or a separate display-only calculation path.
"""

from pathlib import Path

import pytest
from optimization_collectible_cases import expected_cash, flat
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch


@pytest.fixture
def app():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.selectbox[0].set_value("Gold treated as collectible sale timing").run()
    assert not app.exception and not app.error
    return app


def test_gold_starter_discloses_classification_and_preserves_defaults(app):
    """A convenient preset cannot waive the horizon or silently infer gold-fund eligibility."""
    text = app.text_area("policy_search_editor").value
    assert text is not None
    case = PolicySearch.model_validate_json(text)
    assert case.household.lot_plan is not None
    assert case.household.lot_plan.case.securities[0].kind == "collectible"
    assert sum(a.balance for a in case.household.accounts) == 300000
    targets = case.targets
    assert (targets.target_age, targets.success_fraction, targets.reserve_years) == (100, 0.95, 2)
    assert any("not a gold-fund tax ruling" in caption.value for caption in app.caption)


def test_gold_ui_executes_the_same_native_after_tax_cash_oracle(app):
    app.text_area("policy_search_editor").set_value(flat().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    result = app.session_state["policy_search_result"]
    assert result["evaluated_candidates"] == 2
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == expected_cash()
