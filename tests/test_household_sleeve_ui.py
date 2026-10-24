"""Both household and Markets forms expose actual cash/debt outcomes for the new account book."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_sleeve_form_and_cash_results_are_visible():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(b for b in app.button if b.label == "Load synthetic long-short household").click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert any(s.value == "Long-short household cash and recourse debt" for s in app.subheader)


def test_market_sleeve_form_runs_shared_prices_and_exposes_actual_debt():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("Long-short household").run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    assert any(s.value == "Long-short household cash and recourse debt" for s in app.subheader)
