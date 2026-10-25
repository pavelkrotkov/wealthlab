"""Remount restores a nondefault option preset together with its validated data and result."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_nondefault_options_example_remounts_with_its_own_editor_and_result():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox("products_workbench").set_value("Options overlays").run()
    app.selectbox("option_example").set_value("Collar").run()
    app.button(key="FormSubmitter:option_products-Run dated options").click().run()
    expected = app.session_state["option_Collar_result"]
    app.selectbox("products_workbench").set_value("Long/short economics").run()
    app.selectbox("products_workbench").set_value("Options overlays").run()
    assert app.selectbox("option_example").value == "Collar"
    assert app.session_state["option_Collar_result"] == expected
    assert any("Dated option cash" in item.value for item in app.subheader)
