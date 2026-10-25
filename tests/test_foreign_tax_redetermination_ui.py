"""The original-return workbench executes actual refund/arrears cash and clears stale exports."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def app():
    page = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=90).run()
    page.radio[0].set_value("Cross-border").run()
    next(r for r in page.radio if r.label == "Cross-border workbench").set_value(
        "Original-return refunds"
    ).run()
    return page


def test_original_return_workbench_executes_native_revisions_and_invalidates_bad_inputs():
    page = app()
    page.button[0].click().run()
    assert (len(page.exception), len(page.error)) == (0, 0)
    _, rows = page.session_state["foreign_tax_household_result"]
    assert (
        rows[-1]["foreign_final_source_returns"][2025]["final_result"]["federal"][
            "foreign_tax_credit"
        ]
        == 5500
    )
    assert rows[-1]["foreign_final_source_returns"][2026]["owed"] == dict(federal=0, new_jersey=0)
    page.text_area(key="foreign_tax_household_editor").set_value("{}")
    page.button[0].click().run()
    assert "foreign_tax_household_result" not in page.session_state
    assert page.error
    assert not page.exception
