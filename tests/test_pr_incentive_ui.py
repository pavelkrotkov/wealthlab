"""Actual conditional-incentive form preserves edited cases across workbench choices."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_incentive_ui_runs_both_profiles_and_preserves_their_configurations():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90)
    app.run()
    app.sidebar.radio[0].set_value("Annual tax").run()
    app.selectbox(key="annual_workbench").set_value("Puerto Rico incentives").run()
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[1].value == "$5,385.00"
    app.selectbox(key="pr_incentive_example").set_value("2027 rules: post-move stock gain").run()
    app.button[0].click().run()
    assert app.metric[1].value == "$4,000.00"
    app.selectbox(key="pr_incentive_example").set_value("Legacy US dividends").run()
    assert app.metric[1].value == "$5,385.00"
