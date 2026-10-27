"""The real local UI keeps retirement and source contract choices paired.

The visible starter preserves default safety targets. The original flat case
then demonstrates actual source-matched forfeiture/vesting and independent cash.
"""

from pathlib import Path

import pytest
from optimization_employment_cases import flat
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch


@pytest.fixture
def app():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.selectbox[0].set_value("Source-matched retirement and employer vesting").run()
    assert not app.exception and not app.error
    return app


def test_visible_employment_starter_keeps_sources_choices_and_default_targets(app):
    text = app.text_area("policy_search_editor").value
    assert text is not None
    case = PolicySearch.model_validate_json(text)
    assert len(case.employment_offers) == 2
    assert (case.targets.target_age, case.targets.success_fraction, case.targets.reserve_years) == (
        100,
        0.95,
        2,
    )
    assert sum(a.balance for a in case.household.accounts) == 320000
    assert any("not consequences inferred" in caption.value for caption in app.caption)


def test_source_matched_ui_search_settles_the_independent_cash_outcomes(app):
    app.text_area("policy_search_editor").set_value(flat().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    result = app.session_state["policy_search_result"]
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        272000,
        393081,
    ]
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 393081


def test_real_form_explains_mismatched_retirement_and_source_contract(app):
    data = flat().model_dump(mode="json")
    data["dimensions"][0]["choices"][0]["employment_offer"] = "later"
    app.text_area("policy_search_editor").set_value(
        PolicySearch.model_validate(data).model_dump_json()
    )
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception
    assert app.error and "match every source-profile retirement date" in app.error[0].value
