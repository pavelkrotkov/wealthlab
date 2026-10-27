"""Every retirement JSON editor must accept uploaded UTF-8/BOM input and execute its model.

The fake uploader supplies real bytes, just like Streamlit's UploadedFile.
Checking the editor text catches the original repr bug before model validation.
"""

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from wealthlab.retirement.contribution_example import synthetic as contributions
from wealthlab.retirement.distribution_example import synthetic as withdrawals
from wealthlab.retirement.education_example import synthetic as education
from wealthlab.retirement.hsa_example import synthetic as hsa
from wealthlab.retirement.medicare_example import synthetic as medicare
from wealthlab.retirement.social_example import synthetic as social

CASES = [
    ("Contributions", contributions, "retirement_contributions-Allocate contributions"),
    ("IRA withdrawals", withdrawals, "ira_withdrawals-Project IRA withdrawals"),
    ("HSA", hsa, "hsa_case-Project HSA cash flows"),
    ("Education", education, "education_case-Project education accounts"),
    ("Medicare", medicare, "medicare_case-Project Medicare costs"),
    ("Social Security", social, "social_case-Project Social Security claims"),
]


def workbench(mode="Social Security"):
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=30
    ).run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value(mode).run()
    return app


@pytest.mark.parametrize(("mode", "build", "button"), CASES)
def test_uploaded_case_is_editable_json_and_calculates_without_repr_corruption(mode, build, button):
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=30
    ).run()
    app.sidebar.radio[0].set_value("Retirement").run()
    text = build().model_dump_json(indent=2)
    with patch("streamlit.file_uploader", return_value=BytesIO(b"\xef\xbb\xbf" + text.encode())):
        app.radio(key="retirement_mode").set_value(mode).run()
        assert app.text_area[0].value == text
        app.button(key="FormSubmitter:" + button).click().run()
    assert not app.exception
    assert not app.error
    assert app.metric


def test_bad_upload_reports_an_error_without_opening_a_corrupt_editor():
    raw, message = b"\xff", "UTF-8"
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=30
    ).run()
    app.sidebar.radio[0].set_value("Retirement").run()
    with patch("streamlit.file_uploader", return_value=BytesIO(raw)):
        app.radio(key="retirement_mode").set_value("Social Security").run()
    assert not app.exception
    assert len(app.error) == 1
    assert message in app.error[0].value
    assert not app.text_area
