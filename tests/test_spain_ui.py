"""The real annual form submits edited facts, blocks unknowns and clears invalid stale results."""

from streamlit.testing.v1 import AppTest


def app():
    return AppTest.from_string(
        "from wealthlab.ui.spain import show\nshow()", default_timeout=90
    ).run()


def test_real_spanish_annual_form_submits_and_exports_the_reproduced_assessment():
    view = app()
    view.button[0].click().run()
    assert not view.exception
    assert view.session_state["spain_result"]["income"]["assessment"]["liability"] == 12787
    assert len(view.metric) == 1
    assert any("wealth_liability" in item.value for item in view.json)


def test_invalid_edit_clears_the_previously_computed_spanish_result():
    view = app()
    view.button[0].click().run()
    view.text_area[0].input("{}")
    view.button[0].click().run()
    assert not view.exception
    assert view.error
    assert "spain_result" not in view.session_state
