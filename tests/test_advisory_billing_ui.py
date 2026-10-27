"""Selected JSON exposes explicit billing assumptions and supports a validated edit.

No input file is written. Only the scenario uploader receives original
synthetic bytes. Engine calculation retains actual capital and billing dates.
"""

import json
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from tests.advisory_billing_cases import quarter


@pytest.fixture(scope="module")
def imported():
    source = quarter().model_dump_json().encode()
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()

    def selected(label, **kwargs):
        return BytesIO(source) if label == "Load scenario JSON" else None

    with patch("streamlit.file_uploader", side_effect=selected):
        app.run()
        next(b for b in app.button if b.label == "Load selected scenario").click().run()
    text = str(app.text_area(key="advisory_editor").value)
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception and not app.error
    return app, text, app.session_state["projection"][-1]


def test_selected_contract_import_runs_actual_whole_base_fixed_quarter_bill(imported):
    _, text, original = imported
    assert '"rate_application": "whole_relationship_breakpoint"' in text
    assert '"fixed_annual_period_fraction": "0.25"' in text
    assert original["advisory_fees_paid"] == 23
    assert original["closing_cash"] == 977


def test_editable_imported_rate_method_reexecutes_without_changing_capital_or_dates(imported):
    app, text, _ = imported
    edited = json.loads(text)
    edited["schedules"][0].update(
        rate_application="progressive_marginal",
        whole_relationship_breakpoints_source_confirmed=False,
    )
    app.text_area(key="advisory_editor").set_value(json.dumps(edited))
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception and not app.error
    final = app.session_state["projection"][-1]
    assert final["advisory_fees_paid"] == 43
    assert final["closing_cash"] == 957
    assert final["advisory_fee_assessments"][0]["date"] == "2026-03-31"
