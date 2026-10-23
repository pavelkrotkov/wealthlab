"""Exercise the public local verification screen through Streamlit's UI harness."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_verification_screen():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run(timeout=180)
    assert not app.exception
    assert app.title[0].value == "Wealthlab"
    app.button[0].click().run(timeout=180)
    assert not app.exception
    assert app.success[0].value == "All selected engine checks passed."
