"""An optional subscription that received no cash owns no stock; missing calls are not proof."""

import pytest
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.optimization.qoz_exits import completed


@pytest.fixture(scope="module")
def unfunded():
    data = flat().model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    # Actual source crash sale rounds subcent proceeds tozero; no tax benefit supplies cash.
    data["lot_plan"]["case"]["trades"][0]["price"] = ".00000001"
    household = Scenario.model_validate(data)
    return household, project(household)[-1]


def test_actual_never_funded_optional_call_has_no_interest_or_settlement_to_exit(unfunded):
    household, row = unfunded
    audit = row["qoz_audit"]
    assert audit["calls"][0]["funded"] == 0
    assert audit["tranches"] == [] and audit["ending_entity"] is None
    assert row["closing_cash"] == 0
    assert completed(household, row)
