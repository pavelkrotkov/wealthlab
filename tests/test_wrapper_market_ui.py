"""The actual Markets form runs a wrapper-only household without fictitious taxable holdings."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_wrapper_account_scope_and_coverage_are_visible():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("IRA and education proxies").run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    assert any(
        s.value == "Wrapper market proxies and concentration coverage" for s in app.subheader
    )
    result = app.session_state["market_household_result"]["baseline"]
    assert result["household"]["lot_plan"] is None
    assert result["details"][0]["rows"][-1]["account_balances"]["college"] > 0
