"""The conversion/lookback example is runnable through the real household form."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_medicare_ui_shows_paid_premiums_and_zero_owed():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(b for b in app.button if b.label == "Load synthetic Medicare household").click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$515,076.90"
    assert any(m.label == "Medicare premiums paid" and m.value == "$35,855.40" for m in app.metric)
    assert any("already included in healthcare" in c.value for c in app.caption)
