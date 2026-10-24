"""A fresh baseline import replaces edited assumptions and invalidates their previous result."""

import json
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

import pytest

from tests.test_retirement_upload_ui import CASES, workbench


@pytest.mark.parametrize(("mode", "build", "button"), CASES)
def test_baseline_upload_replaces_a_previously_calculated_edit(mode, build, button):
    app = workbench(mode)
    original = build().model_dump_json(indent=2)
    data = json.loads(original)
    field = "opening_cash" if "opening_cash" in data else "start_year"
    data[field] = int(Decimal(str(data[field]))) + 1
    edited = json.dumps(data, indent=2)
    app.text_area[0].set_value(edited)
    app.button(key="FormSubmitter:" + button).click().run()
    assert app.metric
    # Equal starter text still represents a new source selection. Comparing
    # only the file contents used to leave the edited, calculated case active.
    with patch("streamlit.file_uploader", return_value=BytesIO(original.encode())):
        app.run()
        assert app.text_area[0].value == original
        assert not app.metric
        app.button(key="FormSubmitter:" + button).click().run()
    assert not app.exception
    assert not app.error


@pytest.mark.parametrize(("mode", "build", "button"), CASES)
def test_invalid_submission_removes_previous_financial_result(mode, build, button):
    app = workbench(mode)
    app.button(key="FormSubmitter:" + button).click().run()
    assert app.metric
    app.text_area[0].set_value("not JSON")
    app.button(key="FormSubmitter:" + button).click().run()
    assert not app.exception
    assert app.error
    assert not app.metric
