"""The annual workbench selects a new region and retains its actual tax/source outputs."""

from streamlit.testing.v1 import AppTest


def test_all_common_regions_are_editable_and_valencia_uses_its_2025_wealth_minimum():
    view = AppTest.from_string(
        "from wealthlab.ui.spain import show\nshow()", default_timeout=90
    ).run()
    assert len(view.selectbox[0].options) == 15
    view.selectbox[0].select("valencia").run()
    view.button[0].click().run()
    assert not view.exception
    result = view.session_state["spain_result"]
    assert result["wealth"]["assessment"]["wealth_minimum"] == 1000000
    assert "comunitat-valenciana" in result["regional_policy"]["income_source"]
    assert len(view.metric) == 1


def test_galicia_unknown_relief_renders_income_but_no_combined_tax_metric():
    view = AppTest.from_string(
        "from wealthlab.ui.spain import show\nshow()", default_timeout=90
    ).run()
    view.selectbox[0].select("galicia").run()
    view.button[0].click().run()
    assert not view.exception
    assert view.session_state["spain_result"]["income"]["status"] == "conditional"
    assert view.error
    assert not view.metric
