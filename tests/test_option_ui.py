"""The real product workspace runs all three original synthetic contract examples."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.parametrize("strategy", ["Covered call", "Collar", "Four-leg synthetic exposure"])
def test_option_workspace_runs_dated_contracts_and_export(strategy):
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox("products_workbench").set_value("Options overlays").run()
    app.selectbox("option_example").set_value(strategy).run()
    app.button(key="FormSubmitter:option_products-Run dated options").click().run()
    assert not app.exception and not app.error
    result = app.session_state[f"option_{strategy}_result"]
    assert result["ending"]["shares"] == 0
    assert len(result["stress"]) == 9
    assert any("Dated option cash" in item.value for item in app.subheader)


def test_switching_strategy_hides_the_other_case_and_restores_edited_validated_input():
    import json

    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox("products_workbench").set_value("Options overlays").run()
    editor = app.text_area("option_Covered call_editor")
    assert isinstance(editor.value, str)
    data = json.loads(editor.value)
    data["legs"][0]["premium"] = "11"
    edited = json.dumps(data)
    editor.set_value(edited)
    app.button(key="FormSubmitter:option_products-Run dated options").click().run()
    app.selectbox("option_example").set_value("Collar").run()
    assert not any("Dated option cash" in item.value for item in app.subheader)
    app.selectbox("products_workbench").set_value("Long/short economics").run()
    app.selectbox("products_workbench").set_value("Options overlays").run()
    app.selectbox("option_example").set_value("Covered call").run()
    assert app.text_area("option_Covered call_editor").value == edited
