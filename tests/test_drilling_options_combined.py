"""Actual option cash funds drilling without double counting either assets or tax benefits.

Opening wealth is $109,500. Drilling loses $71,200, the covered stock/call earns
$1,500, and no living spending is requested: $39,800 remains before actual tax.
"""

from drilling_option_cases import blended
from streamlit.testing.v1 import AppTest

from wealthlab.household.projection import project


def test_released_option_premium_funds_call_and_both_books_reconcile_after_tax():
    rows = project(blended())
    first, last = rows[0], rows[-1]
    assert (first["drilling_call_funded"], first["drilling_call_owed"]) == (100000, 0)
    assert sum(row["drilling_recourse_funded"] for row in rows) == 0
    assert last["net_wealth"] + last["annual_tax"]["total_liability"] == 39800
    assert (last["drilling_account_value"], last["account_balances"]["options"]) == (22200, 0)
    assert ("drilling_audit" in last, "option_audit" in last) == (True, True)


def test_generic_household_results_render_both_books_and_preserve_nested_audits():
    data = blended().model_dump_json()
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
