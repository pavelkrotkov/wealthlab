"""Real editable Household/Markets flows expose fee assumptions, assessments and paid cash."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_form_edits_sourced_marginal_fee_contracts_and_renders_paid_cash():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.checkbox(key="advisory_enabled").check()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert '"accrual_end"' in str(app.text_area(key="advisory_editor").value)
    assert not app.exception
    assert not app.error
    assert any(s.value == "Outer advisory assessments and actual fee cash" for s in app.subheader)


def test_shared_market_fee_starter_executes_the_same_native_ledger_and_audit():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.checkbox(key="market_advisory_example").check().run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    final = app.session_state["market_household_result"]["baseline"]["details"][0]["rows"][-1]
    assert final["advisory_fee_audit"]["assessments"]
    assert any(s.value == "Outer advisory assessments and actual fee cash" for s in app.subheader)
