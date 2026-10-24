"""The market form actually applies independently selected synthetic loss treatments."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_user_can_allow_federal_losses_while_denying_nj_losses_in_actual_return():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("Long-short household").run()
    app.checkbox(key="sleeve_loss_example").check().run()
    next(s for s in app.selectbox if s.label == "Synthetic federal loss treatment").set_value(
        "allowed"
    ).run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["market_household_result"]["baseline"]
    rows = result["details"][0]["rows"]
    assert rows[11]["annual_tax"]["federal"]["agi"] == 57000
    audit = rows[-1]["sleeve_tax_assumptions"][0]
    assert (audit["federal_loss"]["treatment"], audit["new_jersey_loss"]["treatment"]) == (
        "allowed",
        "denied",
    )
