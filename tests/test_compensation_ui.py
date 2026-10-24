"""Both the ordinary employer scenario and explicit linked shock run through the household UI."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.parametrize(
    ("button", "expected"),
    [
        ("Load synthetic employer compensation household", "$295,980.00"),
        ("Load synthetic linked employment and asset shock", "$204,754.50"),
    ],
)
def test_compensation_households_show_value_liquidity_and_conditional_tax_scope(button, expected):
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(b for b in app.button if b.label == button).click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == expected
    assert any(s.value == "Employer-linked value and liquidity" for s in app.subheader)
    assert any("hypothetical exit tax remain unmodeled" in c.value for c in app.caption)
