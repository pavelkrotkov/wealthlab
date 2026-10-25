"""The editable product comparison runs and never retains results after invalid assumptions."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_comparison_form_renders_matched_wealth_and_clears_invalid_protection_price():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox("products_workbench").set_value("Whole life versus liquid saving").run()
    app.button(
        key="FormSubmitter:life_comparison_entered-Compare actual insurance alternatives"
    ).click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["life_comparison_entered_result"]
    assert result["alternatives"]["liquid_term"]["outcomes"][0]["closing_cash"] == 4900
    assert len(app.dataframe) >= 2
    editor = app.text_area("life_comparison_entered_editor")
    assert isinstance(editor.value, str)
    data = json.loads(editor.value)
    data["independently_priced_protection_confirmed"] = False
    editor.set_value(json.dumps(data))
    app.button(
        key="FormSubmitter:life_comparison_entered-Compare actual insurance alternatives"
    ).click().run()
    assert app.error
    assert "life_comparison_entered_result" not in app.session_state
