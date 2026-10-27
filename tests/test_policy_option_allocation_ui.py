"""Actual UI controls export fixed unit assumptions and execute real option purchases.

The default95percent/age100 safety targets remain unchanged by the starter.
Whole existing option positions and new-unit purchases are exclusive modes.
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
    return app


def test_option_allocation_starter_preserves_targets_and_exports_a_cash_only_unit(app):
    app.checkbox("new_option_allocation_starter").set_value(True).run()
    encoded = app.text_area("policy_search_editor").value
    assert encoded is not None
    offered = PolicySearch.model_validate_json(encoded)
    assert offered.targets.success_fraction == 0.95 and offered.targets.target_age == 100
    assert offered.option_opportunity and not offered.option_opportunity.unit.case.holdings.lots
    assert offered.option_opportunity.owner == "joint"
    assert [c.option_units for c in offered.dimensions[-1].choices] == [0, 1, 2]


def test_existing_contract_starter_disables_new_purchase_instead_of_overwriting_the_book(app):
    app.checkbox("Add synthetic options and employer contract exits").set_value(True).run()
    assert app.checkbox("new_option_allocation_starter").disabled
    assert not app.exception and not app.error
