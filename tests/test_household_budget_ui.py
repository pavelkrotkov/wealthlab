"""Actual Household form edits quote assumptions without creating forecast income or payments."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from tests.household_budget_cases import synthetic


def submit(app):
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    return app.session_state["projection"][-1]


def lower_forecast(app):
    editor = next(
        field
        for field in app.text_area
        if field.label == "Linked lot book, monthly marks and funding permissions (JSON)"
    )
    raw = editor.value
    assert raw is not None
    data = json.loads(raw)
    annual = data["tax_budget_forecasts"][0]["cases"][0]
    annual["federal_income"]["wages_primary"] = "100000"
    annual["nj_income"]["wages"] = "100000"
    editor.set_value(json.dumps(data))


def test_editable_forecast_changes_sale_but_actual_tax_and_income_remain_native():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=90)
    app.session_state["scenario"] = synthetic()
    app.run()
    first = submit(app)
    assert first["closing_cash"] < 6000
    assert any(item.value == "Tax-budget estimates and actual return" for item in app.subheader)
    # The changed assumption may alter a sale, but cannot generate its bonus.
    lower_forecast(app)
    second = submit(app)
    assert second["closing_cash"] == second["net_wealth"] == 11000
    assert second["lot_audit"]["sale_decisions"][0]["sold_units"] == 100
    assert second["annual_tax"]["federal"]["agi"] == 5000
    assert second["lot_audit"]["budget_audit"][0]["actual_total_liability"] == 0
