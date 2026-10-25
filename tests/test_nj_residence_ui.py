"""The actual Cross-border route edits NJ facts, calculates returns and executes one wallet."""

from decimal import Decimal
from pathlib import Path

from streamlit.testing.v1 import AppTest


def app():
    page = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=90).run()
    page.radio[0].set_value("Cross-border").run()
    next(r for r in page.radio if r.label == "Cross-border workbench").set_value(
        "NJ residence / move"
    ).run()
    return page


def test_editable_nj_annual_workbench_has_actual_resident_and_nonresident_calculations():
    page = app()
    page.button[0].click().run()
    assert (len(page.exception), len(page.error)) == (0, 0)
    _, result = page.session_state["nj_residence_annual_result"]
    assert result["new_jersey"]["income_tax"] == Decimal("1741.60")
    assert any("Separate NJ return" in s.value for s in page.subheader)


def test_household_nj_and_foreign_workbench_runs_real_cash_and_clears_invalid_replacement():
    page = app()
    next(r for r in page.radio if r.label == "NJ residence calculation").set_value(
        "Household cash"
    ).run()
    page.button[0].click().run()
    assert (len(page.exception), len(page.error)) == (0, 0)
    _, rows = page.session_state["nj_residence_household_result"]
    assert rows[-1]["closing_cash"] == Decimal("30533.90")
    page.text_area(key="nj_residence_household_editor").set_value("{}")
    page.button[0].click().run()
    assert "nj_residence_household_result" not in page.session_state
    assert page.error
    assert not page.exception
