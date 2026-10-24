"""The actual Products form exposes a usable economic comparison without claiming tax benefits."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_products_form_runs_paired_long_short_economics():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Products").run()
    app.button(key="FormSubmitter:long_short-Compare long/short economics").click().run()
    assert not app.exception
    assert not app.error
    assert any(s.value == "Paired pre-tax economic outcomes" for s in app.subheader)
    result = app.session_state["long_short_result"]
    assert result["sleeve"]["batch_id"] == result["reference"]["batch_id"]
    assert "Pre-tax" in result["sleeve"]["scope"]
