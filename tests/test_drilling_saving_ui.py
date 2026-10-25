"""Generic Household retains saving lots and drilling basis audits without numeric coercion."""

from drilling_saving_cases import blended
from streamlit.testing.v1 import AppTest


def test_shared_saving_and_drilling_audits_render_in_the_actual_household_results():
    source = "\n".join(
        [
            "from wealthlab.household.scenario import Scenario",
            "from wealthlab.household.projection import project",
            "from wealthlab.ui.results import display",
            f"case = Scenario.model_validate_json({blended().model_dump_json()!r})",
            "display(case, project(case))",
        ]
    )
    view = AppTest.from_string(source, default_timeout=90).run()
    assert (bool(view.exception), bool(view.error)) == (False, False)
    assert any("basis_effects" in item.value for item in view.json)
    assert any("saving" in item.value for item in view.json)
