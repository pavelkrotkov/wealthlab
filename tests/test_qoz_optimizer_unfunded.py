"""An optional subscription that received no cash owns no stock; missing calls are not proof."""

from copy import deepcopy

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


@pytest.mark.parametrize(
    "change", ["missing_calls", "wrong_call", "funded", "unobserved_call", "interest"]
)
def test_zero_mark_cannot_hide_a_missing_or_positive_call_or_remaining_interest(unfunded, change):
    household, original = unfunded
    row = deepcopy(original)
    audit = row["qoz_audit"]
    if change == "missing_calls":
        audit["calls"] = None
    elif change == "wrong_call":
        audit["calls"][0]["call"]["id"] = "unknown"
    elif change == "funded":
        audit["calls"][0]["funded"] = 1
    elif change == "unobserved_call":
        audit["calls"] = []
    else:
        audit["tranches"] = [dict(funded=1)]
    assert not completed(household, row)
