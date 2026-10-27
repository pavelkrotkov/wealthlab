"""A blocked wealth classification is visible in the actual annual-plan UI."""

import json

from streamlit.testing.v1 import AppTest


def test_blocked_wealth_preserves_income_audit_and_suppresses_combined_tax_metric():
    view = AppTest.from_string(
        "from wealthlab.ui.spain_assessments import show\nshow()", default_timeout=90
    ).run()
    edited = view.text_area[0].value
    assert isinstance(edited, str)
    data = json.loads(edited)
    data["annuals"][0]["case"]["assets"][0]["treatment"] = "unknown"
    view.text_area[0].input(json.dumps(data))
    view.button[0].click().run()
    result = view.session_state["spain_assessments_result"]
    assert not view.exception
    assert view.error
    assert not view.metric
    assert result["assessments"]["person_a_2025"]["liabilities_eur"]["irpf"] == 12787
