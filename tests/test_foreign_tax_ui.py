"""The actual app executes foreign tax cash and clears invalid edits before export.

Both the Cross-border JSON workbench and ordinary Household form run the same
wallet and native annual calculation. Displayed foreign payments cannot be a
standalone illustration. Invalid edits remove earlier cash/credit results so
that an old favorable export cannot survive an incomplete replacement input.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app():
    case = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=90).run()
    case.radio[0].set_value("Cross-border").run()
    next(r for r in case.radio if r.label == "Cross-border workbench").set_value(
        "Household foreign taxes"
    ).run()
    return case


def test_generic_household_form_retains_foreign_plan_and_reports_the_same_cash_engine():
    app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=90).run()
    next(b for b in app.button if b.label == "Load synthetic foreign-tax household").click().run()
    next(b for b in app.button if b.label == "Validate and project").click().run()
    rows = app.session_state["projection"]
    assert not app.exception
    assert rows[0]["foreign_tax_paid"] == 11000
    assert app.session_state["scenario"].foreign_tax_plan is not None
