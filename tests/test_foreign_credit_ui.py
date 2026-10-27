"""Actual editable source/FX form submits tax results and clears invalid stale output."""

import json
from decimal import Decimal
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app():
    instance = AppTest.from_file(
        str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90
    )
    instance.run()
    instance.sidebar.radio[0].set_value("Cross-border").run()
    return instance


def test_actual_source_payment_form_runs_native_credit_and_exports_complete_audit(app):
    app.button[0].click().run()
    result = app.session_state["foreign_credit_result"]
    assert not app.exception
    assert result["candidate"]["federal"]["foreign_tax_credit"] == Decimal("6724.50")
    assert result["observed_tax_cash_outflow_usd"] == Decimal(11000)
    assert len(app.dataframe) >= 2


def test_unknown_eligibility_retains_actual_cash_without_a_favorable_credit(app):
    data = json.loads(app.text_area(key="foreign_credit_editor").value)
    data["eligibility"] = "unresolved"
    app.text_area(key="foreign_credit_editor").set_value(json.dumps(data))
    app.button[0].click().run()
    result = app.session_state["foreign_credit_result"]
    assert not app.exception
    assert result["candidate"] is None
    assert result["observed_tax_cash_outflow_usd"] == Decimal(11000)


def test_invalid_edit_clears_the_previous_credit_result(app):
    app.button[0].click().run()
    app.text_area(key="foreign_credit_editor").set_value("{")
    app.button[0].click().run()
    assert app.error
    assert not app.exception
    with pytest.raises(KeyError):
        app.session_state["foreign_credit_result"]
