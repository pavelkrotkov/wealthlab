"""Limited installations disclose required retirement data before submitting a case."""

from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.parametrize("module", ["household", "retirement_workspace"])
def test_missing_owl_tables_are_visible_before_running_a_profile(module):
    with patch("wealthlab.ui.optional_dependencies.find_spec", return_value=None):
        view = AppTest.from_string(f"from wealthlab.ui.{module} import show\nshow()").run(
            timeout=90
        )
    assert not view.exception
    assert any("Limited installation" in item.value and "RMD" in item.value for item in view.info)
