"""The real multi-year/person form renders reconciled schedules and clears invalid stale results."""

import json

from streamlit.testing.v1 import AppTest


def app():
    return AppTest.from_string(
        "from wealthlab.ui.spain_assessments import show\nshow()", default_timeout=90
    ).run()


def test_excessive_schedule_renders_blocked_while_annual_assessments_remain_visible():
    view = app()
    data = json.loads(view.text_area[0].value)
    data["obligations"][0]["amount_eur"] = "999999"
    view.text_area[0].input(json.dumps(data))
    view.button[0].click().run()
    assert not view.exception
    assert view.error
    assert view.session_state["spain_assessments_result"]["obligations"][0]["fundable_eur"] is None
    # The invalid schedule does not erase its independently resolved annual tax.
    assert view.metric
