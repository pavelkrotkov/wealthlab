"""The transition form displays a real original-year revision beside its delayed refund."""

from pathlib import Path

from qoz_transition_cases import transition
from streamlit.testing.v1 import AppTest


def test_transition_profile_submits_and_displays_source_year_corrections():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()
    app.radio[0].set_value("Products").run()
    app.selectbox(key="products_workbench").set_value("Opportunity-zone funds").run()
    app.selectbox[1].set_value("2026 gain / 2027 investment").run()
    app.text_area(key="qoz_editor").set_value(transition().model_dump_json())
    app.button(key="FormSubmitter:qoz-Compare QOZ tax and liquidity").click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["qoz_result"]
    assert result["rows"]["allowed"][-1]["qoz_audit"]["source_return_revisions"]
    assert result["rows"]["denied"][-1]["qoz_audit"]["source_return_revisions"] == []
    assert any("Prior cash rows remain historical" in caption.value for caption in app.caption)
