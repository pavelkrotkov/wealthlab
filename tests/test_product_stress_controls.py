"""A named stress cannot look active in a mode that does not apply its overlay."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.parametrize("workspace,prefix", [("Products", "Product"), ("Markets", "Synthetic")])
def test_stress_selector_is_enabled_only_when_stress_mode_is_selected(workspace, prefix):
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.radio[0].set_value(workspace).run()
    mode = next(s for s in app.selectbox if s.label == f"{prefix} market mode")
    stress = next(s for s in app.selectbox if s.label == f"{prefix} named stress")
    assert stress.disabled
    mode.set_value("stress").run()
    assert not next(s for s in app.selectbox if s.label == f"{prefix} named stress").disabled
