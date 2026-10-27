"""A native full-horizon starter exposes recurring wages/spending without inventing private facts.

The short composable examples keep their original role. The full case has its
own complete schedules and labels its small training/validation samples honestly.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from wealthlab.optimization.inputs import PolicySearch


@pytest.fixture
def app():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=180
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.selectbox[0].set_value("Full age-100 cash and stock example").run()
    for field, value in zip(app.number_input, (1800000, 6000, 2500, 100), strict=True):
        field.set_value(value)
    app.run()
    return app


def test_native_full_horizon_form_updates_cash_wages_spending(app):
    assert not app.exception and not app.error
    text = app.text_area("policy_search_editor").value
    assert isinstance(text, str)
    profile = PolicySearch.model_validate_json(text)
    assert str(profile.household.end) == "2078-01-01"
    assert profile.household.accounts[0].balance == 1800000
    assert profile.household.incomes[0].monthly_amount == 6000
    assert profile.household.expenses[0].monthly_amount == 2500
