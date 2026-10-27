"""Actual retained-source holding dates determine year-boundary character independently of basis."""

from datetime import date

import pytest
from exchange_allocation_cases import allocated

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


@pytest.mark.parametrize(
    ("acquired", "character"), [("2025-12-31", "short_term"), ("2025-12-30", "long_term")]
)
def test_source_sale_preserves_actual_holding_date_and_each_basis(acquired, character):
    data = allocated(0).model_dump(mode="json")
    data["exchange_fund_plan"]["source_lot"].update(
        acquired=acquired, federal_holding_start=acquired
    )
    audit = project(Scenario.model_validate(data))[-1]["exchange_fund_audit"]
    sale = audit["disposals"][0]
    assert sale["acquired"] == date.fromisoformat(acquired)
    assert sale["federal_holding_start"] == acquired
    assert sale["federal_character"] == character
    assert (sale["federal_basis"], sale["nj_basis"]) == (20000, 30000)
    assert sale["proceeds"] == 100000
