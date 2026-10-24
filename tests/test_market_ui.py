"""All four market modes run through the real UI with explicit scope limits."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.parametrize(
    "mode,paths",
    [("deterministic", "1"), ("historical", "1"), ("monte_carlo", "250"), ("stress", "1")],
)
def test_market_paths_ui_generates_exportable_batches(mode, paths):
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.sidebar.radio[0].set_value("Markets").run()
    app.selectbox[0].set_value(mode).run()
    next(b for b in app.button if b.label == "Generate market paths").click().run()
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert metrics == {"Realized paths": paths, "Months per path": "120", "Market factors": "3"}
    assert any("do not measure spending success" in w.value for w in app.warning)
