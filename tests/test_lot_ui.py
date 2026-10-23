"""The synthetic lot workbench runs through the same engine as programmatic cases."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_lot_workbench_reports_gross_scope_and_partial_sale():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Tax lots").run()
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$10,995.00"
    assert "Gross lot accounting only" in app.warning[0].value
