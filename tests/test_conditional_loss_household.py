"""Conditional loss timing changes one actual return, never a fictitious tax-savings receipt."""

import pytest
from conditional_loss_cases import allocation
from household_sleeve_cases import change, flat

from wealthlab.household.projection import project


@pytest.mark.parametrize(
    "treatment,agi", [("allowed", 38000), ("denied", 50000), ("deferred", 50000)]
)
def test_supplied_losses_use_annual_limits_and_horizon_without_duplicate_cash(treatment, agi):
    def configure(data):
        data["sleeve_plan"]["sleeves"][0]["allocations"] = [
            allocation(treatment).model_dump(mode="json")
        ]

    rows = project(change(flat(100000), configure))
    final = rows[-1]
    assert final["annual_tax"]["federal"]["agi"] == agi
    assert sum(r["tax_event_cash"] for r in rows) == 0
    assert final["net_wealth"] == 200000 - final["annual_tax"]["total_liability"]
    assert final["sleeve_tax_assumptions"][0]["federal_loss"]["treatment"] == treatment
    assert final["annual_tax"]["new_jersey"]["gross_income"] == 50000
