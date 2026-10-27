"""Only freshly generated synthetic menus finish their complete scope after adding all builders."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.validation import validate


def test_generated_scope_is_complete_and_later_fee_edits_require_confirmation():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.checkbox("qoz_starter").set_value(True).run()
    app.checkbox("drilling_starter").set_value(True).run()
    app.checkbox("optimizer_advisory_starter").set_value(True).run()
    assert not app.error and not app.exception
    text = app.text_area("policy_search_editor").value
    assert text is not None
    profile = PolicySearch.model_validate_json(text)
    assert validate(profile) == 24
    assert profile.household.advisory_fee_plan is not None
    changed = profile.model_dump(mode="json")
    changed["household"]["advisory_fee_plan"]["schedules"][0]["fixed_per_period"] = "1"
    with pytest.raises(ValueError, match="new independently sourced envelope"):
        validate(PolicySearch.model_validate(changed))
