"""The actual Cross-border route edits country facts and executes the existing shared wallet.

Both country modes run from editable native source facts. Invalid replacement
inputs must remove the prior calculation and its export, including when the
previous scenario had enough cash to pay every tax in the comparison.
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def app():
    page = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=90).run()
    page.radio[0].set_value("Cross-border").run()
    next(r for r in page.radio if r.label == "Cross-border workbench").set_value(
        "Country cash"
    ).run()
    return page


def test_native_pr_household_workbench_executes_calculated_bill_and_clears_bad_replacement():
    page = app()
    page.button[0].click().run()
    assert (len(page.exception), len(page.error)) == (0, 0)
    _, result = page.session_state["jurisdiction_execution_pr_result"]
    assert not result["rows"][-1]["funding_failure"]
    assert (
        result["reconciliation"][-1]["assessments"]
        == result["reconciliation"][-1]["revised_assessments"]
    )
    page.text_area(key="jurisdiction_execution_pr_editor").set_value("{}")
    page.button[0].click().run()
    assert "jurisdiction_execution_pr_result" not in page.session_state
    assert page.error
    assert not page.exception


def test_native_spain_workbench_uses_actual_paid_ip_and_exports_real_foreign_cash():
    page = app()
    next(r for r in page.radio if r.label == "Country execution example").set_value("Spain").run()
    page.button[0].click().run()
    assert (len(page.exception), len(page.error)) == (0, 0)
    _, result = page.session_state["jurisdiction_execution_es_result"]
    assert result["country_assessments"]["person_a_2025"]["outstanding_eur"] == dict(
        irpf=0, wealth=0, solidarity=0
    )
    assert result["rows"][-1]["foreign_tax_paid"] > 0
    assert any("actual paid-tax reconciliation" in s.value for s in page.subheader)
