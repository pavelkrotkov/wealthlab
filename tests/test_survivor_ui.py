"""The survivor examples execute through the same fixed-date claim workbench."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.parametrize(
    ("example", "expected"),
    [("Survivor then own claim", "$234,772.00"), ("Early-worker survivor limit", "$82,980.00")],
)
def test_survivor_examples_report_native_cash_and_exclude_incompatible_reference(example, expected):
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("Social Security").run()
    app.selectbox(key="social_example").set_value(example).run()
    app.button(key="FormSubmitter:social_case-Project Social Security claims").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == expected
