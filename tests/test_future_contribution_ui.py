"""Forward contribution assumptions are editable, runnable and visibly conditional."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from tests.future_contribution_cases import hsa, retirement


@pytest.mark.parametrize(
    "mode,case,key,button",
    [
        (
            "Contributions",
            retirement,
            "retirement_editor",
            "FormSubmitter:retirement_contributions-Allocate contributions",
        ),
        ("HSA", hsa, "hsa_editor", "FormSubmitter:hsa_case-Project HSA cash flows"),
    ],
)
def test_forward_rule_mode_is_visible_in_results(mode, case, key, button):
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=45
    ).run()
    app.sidebar.radio[0].set_value("Retirement").run()
    if mode == "HSA":
        app.radio(key="retirement_mode").set_value(mode).run()
    app.text_area(key=key).set_value(case().model_dump_json())
    app.button(key=button).click().run()
    assert not app.exception
    assert not app.error
    assert any("2026 · freeze_2026_assumption" in c.value for c in app.caption)
