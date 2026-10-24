"""Manual benefit amounts cannot duplicate generated SSA premium-collection events."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.social_medicare_example import synthetic


@pytest.mark.parametrize("year_index", [0, 1, 2])
def test_manual_annual_benefits_block_in_every_projection_year(year_index):
    data = synthetic().model_dump(mode="json")
    data["tax_plan"]["cases"][year_index]["federal_income"]["social_security"] = "1000"
    message = "exclude generated Social Security" if year_index == 0 else "Future recognized income"
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data))


def test_manual_dated_benefit_event_blocks_before_collection():
    data = synthetic().model_dump(mode="json")
    data["tax_plan"]["events"] = [
        dict(
            date="2030-06-01",
            description="Duplicate manual benefit",
            cash_received="1000",
            federal=dict(social_security="1000"),
            new_jersey={},
        )
    ]
    with pytest.raises(ValueError, match="Remove manual Social Security events"):
        project(Scenario.model_validate(data))


def test_manual_benefit_income_rule_blocks_before_collection():
    data = synthetic().model_dump(mode="json")
    data["tax_plan"]["income_rules"][0].update(federal="social_security", new_jersey="none")
    with pytest.raises(ValueError, match="Remove manual Social Security income rules"):
        project(Scenario.model_validate(data))
