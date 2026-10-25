"""The ordinary household tax table displays the canonical revised source-year liability."""

from qoz_transition_cases import transition
from streamlit.testing.v1 import AppTest


def test_household_tax_table_includes_actual_qoz_source_revision_and_unchanged_cash_history():
    data = transition().model_dump_json()
    source = "\n".join(
        [
            "from wealthlab.household.scenario import Scenario",
            "from wealthlab.household.projection import project",
            "from wealthlab.ui.projected_tax import display",
            f"case = Scenario.model_validate_json({data!r})",
            "display(project(case))",
        ]
    )
    app = AppTest.from_string(source, default_timeout=90).run()
    assert not app.exception
    table = app.dataframe[0].value
    assert table.set_index("year").loc["2026", "total_liability"] == 0
    assert any("source-return" in caption.value for caption in app.caption)
