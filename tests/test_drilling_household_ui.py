"""An imported drilling Scenario also renders in the generic Household results view."""

from drilling_cases import short
from streamlit.testing.v1 import AppTest


def test_household_results_keep_nested_drilling_audits_outside_numeric_plot_frame():
    data = short().model_dump_json()
    source = "\n".join(
        [
            "from wealthlab.household.scenario import Scenario",
            "from wealthlab.household.projection import project",
            "from wealthlab.ui.results import display",
            f"case = Scenario.model_validate_json({data!r})",
            "display(case, project(case))",
        ]
    )
    app = AppTest.from_string(source, default_timeout=90).run()
    assert (bool(app.exception), bool(app.error)) == (False, False)
    assert any("drilling" in item.value for item in app.json)
    assert app.metric[0].value == "$140,000.00"
