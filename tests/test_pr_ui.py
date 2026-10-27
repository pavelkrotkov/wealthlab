"""Real editable annual PR submission and malformed-input recovery."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_pr_subworkbench_calculates_and_recovers_from_invalid_configuration():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90)
    app.run()
    app.sidebar.radio[0].set_value("Annual tax").run()
    app.selectbox(key="annual_workbench").set_value("Puerto Rico annual").run()
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == "$26,031.60"
    app.text_area(key="pr_configuration").set_value("{")
    app.button[0].click().run()
    assert app.error
    app.text_area(key="pr_configuration").set_value(app.session_state["pr_case"].model_dump_json())
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[2].value == "$18,381.60"
