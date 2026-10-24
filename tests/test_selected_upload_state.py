"""Streamlit can reconstruct an UploadedFile without changing its selected file identity."""

import json
from types import SimpleNamespace
from unittest.mock import patch

from tests.test_retirement_upload_ui import workbench
from wealthlab.retirement.social_example import synthetic


def test_same_selected_file_preserves_edits_but_a_new_upload_replaces_them():
    app = workbench()
    original = synthetic().model_dump_json(indent=2)
    data = json.loads(original)
    data["start_year"] = 2031
    uploaded = SimpleNamespace(file_id="first", getvalue=lambda: original.encode())
    with patch("streamlit.file_uploader", return_value=uploaded):
        app.radio(key="retirement_mode").set_value("Social Security").run()
        app.text_area[0].set_value(json.dumps(data, indent=2))
        app.button(key="FormSubmitter:social_case-Project Social Security claims").click().run()
    assert app.metric[0].value == "$104,400.00"
    reconstructed = SimpleNamespace(file_id="first", getvalue=lambda: original.encode())
    with patch("streamlit.file_uploader", return_value=reconstructed):
        app.run()
    assert json.loads(app.text_area[0].value)["start_year"] == 2031
    assert app.metric[0].value == "$104,400.00"
    replacement = SimpleNamespace(file_id="replacement", getvalue=lambda: original.encode())
    with patch("streamlit.file_uploader", return_value=replacement):
        app.run()
    assert app.text_area[0].value == original
    assert not app.metric


def test_returning_to_a_workbench_restores_the_last_validated_case():
    app = workbench()
    data = json.loads(app.text_area[0].value)
    data["start_year"] = 2031
    app.text_area[0].set_value(json.dumps(data))
    app.button(key="FormSubmitter:social_case-Project Social Security claims").click().run()
    app.radio(key="retirement_mode").set_value("HSA").run()
    app.radio(key="retirement_mode").set_value("Social Security").run()
    assert json.loads(app.text_area[0].value)["start_year"] == 2031
    assert app.metric[0].value == "$104,400.00"
