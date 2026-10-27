"""Drive the actual country cash workspace before inspecting calculated result state."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def app(choice):
    page = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=90).run()
    page.radio[0].set_value("Cross-border").run()
    next(r for r in page.radio if r.label == "Cross-border workbench").set_value(
        "Country cash"
    ).run()
    next(r for r in page.radio if r.label == "Country execution example").set_value(choice).run()
    return page
