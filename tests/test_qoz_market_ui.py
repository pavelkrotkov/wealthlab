"""The editable actual Markets workflow exposes native fund cash beside the realized batch."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_actual_qoz_market_form_runs_with_editable_binding_and_native_cash_table():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("Opportunity-zone household").run()
    assert '"net_entity_tax_pre_investor_cost_confirmed": true' in str(
        app.text_area(key="market_household_editor").value
    )
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["market_household_result"]["baseline"]
    assert result["aggregate"]["paths"] == 1
    assert any(
        item.value == "QOZ shared asset factor and actual fund cash" for item in app.subheader
    )
