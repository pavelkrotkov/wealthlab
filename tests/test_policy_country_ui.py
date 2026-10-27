"""The original fixed-country preset reaches native candidate tax/cash and keeps its context."""

import json
from decimal import Decimal as D
from pathlib import Path

from country_optimizer_cases import ready
from streamlit.testing.v1 import AppTest

from wealthlab.household.report import encode
from wealthlab.ui.optimization_results import selected_inputs


def test_real_country_optimizer_form_preserves_fixed_context_and_actual_after_tax_cash():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.selectbox[0].set_value("Fixed PR country tax and retirement wages").run()
    original = json.loads(app.text_area("policy_search_editor").value or "{}")
    assert original["country_context"]["wage_sources"][0]["source_id"] == "wage_09"
    app.text_area("policy_search_editor").set_value(ready().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert (len(app.exception), len(app.error)) == (0, 0)
    result = app.session_state["policy_search_result"]
    candidate = result["candidates"][1]
    assert (candidate["median_real_after_tax_exit_wealth"], candidate["median_net_cash_tax"]) == (
        D("56234.95"),
        D("33765.05"),
    )
    exported = selected_inputs(result["held_out"]["results"])
    assert exported["scenario"]["foreign_tax_plan"]["assessments"][0]["country"] == "PR"
    assert exported["scenario"]["tax_plan"]["cases"][0]["pr_federal"]["sources"]
    assert json.loads(encode(result))["inputs"]["country_context"] == original["country_context"]
