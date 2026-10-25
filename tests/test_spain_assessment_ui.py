"""The real multi-year/person form renders reconciled schedules and clears invalid stale results."""

import json

from streamlit.testing.v1 import AppTest


def app():
    return AppTest.from_string(
        "from wealthlab.ui.spain_assessments import show\nshow()", default_timeout=90
    ).run()


def test_real_assessment_plan_form_submits_the_independent_annual_cases():
    view = app()
    view.button[0].click().run()
    assert not view.exception
    assert view.session_state["spain_assessments_result"]["all_obligations_resolved"] is True
    assert view.metric[0].value == "€147,348.67"
    assert any("fundable_eur" in item.value for item in view.json)


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


def test_invalid_assessment_plan_clears_previous_result():
    view = app()
    view.button[0].click().run()
    view.text_area[0].input("{}")
    view.button[0].click().run()
    assert not view.exception
    assert view.error
    assert "spain_assessments_result" not in view.session_state


def test_products_router_opens_the_actual_multi_year_assessment_workbench():
    view = AppTest.from_string(
        "from wealthlab.ui.products import show\nshow()", default_timeout=90
    ).run()
    view.selectbox[0].select("Spain annual tax schedules").run()
    view.button[0].click().run()
    assert not view.exception
    assert len(view.session_state["spain_assessments_result"]["assessments"]) == 3
