"""An edited country clone and a new country selection retain the full native baseline.

Adding1000 opening cash changes cash by1000 under unchanged supplied tax facts.
The baseline keeps the original Spain context after switching to Puerto Rico;
its source assessment must be recomputed rather than replaced by a frozen bill.
"""

import json

from test_jurisdiction_execution_ui import app

from wealthlab import country_report
from wealthlab.household.report import encode


def calculate(page):
    next(
        b for b in page.button if b.label == "Calculate country assessments and cash"
    ).click().run()
    assert (len(page.exception), len(page.error)) == (0, 0)


def select_country(page, name):
    next(r for r in page.radio if r.label == "Country execution example").set_value(name).run()


def test_country_baseline_survives_edited_clone_and_country_selection():
    page = app()
    select_country(page, "Spain")
    calculate(page)
    original, result = page.session_state["jurisdiction_execution_es_result"]
    baseline_wealth = result["rows"][-1]["net_wealth"]
    next(b for b in page.button if b.label.startswith("Keep this scenario")).click().run()
    archive = json.loads(encode(country_report.payload(original, result)))
    archive["months"][-1]["net_wealth"] = "invented cached wealth"
    page.text_area("jurisdiction_execution_es_editor").set_value(json.dumps(archive))
    calculate(page)
    assert (
        page.session_state["jurisdiction_execution_es_result"][1]["rows"][-1]["net_wealth"]
        == baseline_wealth
    )
    edited = original.model_dump(mode="json")
    edited["scenario"]["accounts"][0]["balance"] = "201000"
    page.text_area("jurisdiction_execution_es_editor").set_value(json.dumps(edited))
    calculate(page)
    assert page.session_state["baseline"] == original
    assert page.metric[-1].value == "$1,000.00"
    select_country(page, "Puerto Rico")
    calculate(page)
    assert page.session_state["baseline"].spain == original.spain
    _, candidate = page.session_state["jurisdiction_execution_pr_result"]
    delta = candidate["rows"][-1]["net_wealth"] - baseline_wealth
    assert page.metric[-1].value == f"${delta:,.2f}"
