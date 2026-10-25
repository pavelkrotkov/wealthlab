"""The added product switch must preserve existing long/short validated work."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_product_remount_preserves_nondefault_long_short_mode_edited_input_and_result():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Products").run()
    by_label(app, "Product market mode").set_value("monte_carlo").run()
    editor = app.text_area("long_short_editor")
    assert isinstance(editor.value, str)
    data = json.loads(editor.value)
    data["market"]["seed"] = 321
    edited = json.dumps(data)
    editor.set_value(edited)
    app.button(key="FormSubmitter:long_short-Compare long/short economics").click().run()
    expected = app.session_state["long_short_result"]
    app.selectbox("products_workbench").set_value("Options overlays").run()
    app.selectbox("products_workbench").set_value("Long/short economics").run()
    mode = by_label(app, "Product market mode")
    assert mode.value == "monte_carlo"
    assert app.text_area("long_short_editor").value == edited
    assert app.session_state["long_short_result"] == expected


def by_label(app, label):
    return next(item for item in app.selectbox if item.label == label)
