"""Invalid identity, access and eligibility fail before any source assets move."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_rollover_example import synthetic


@pytest.mark.parametrize(
    "field,value",
    [
        ("source", "ira"),
        ("destination", "work_pretax"),
        ("date", "2026-02-02"),
        ("date", "2025-12-01"),
        ("provenance", "unresolved"),
        ("id", "ira_draw"),
        ("id", "wlrmd_auto_alias"),
        ("id", "household_ira_funding_alias"),
        ("eligible_direct_cash_rollover_to_same_owner_ordinary_ira_confirmed", False),
    ],
)
def test_unsupported_rollover_requests_fail_closed(field, value):
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["direct_rollovers"][0][field] = value
    with pytest.raises(ValueError):
        project(Scenario.model_validate(data))


def test_a_rollover_cannot_precede_confirmed_source_separation():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["profiles"]["work_pretax"]["separation_date"] = (
        "2026-03-01"
    )
    with pytest.raises(ValueError, match="precede confirmed separation"):
        project(Scenario.model_validate(data))


def test_a_rollover_requires_an_actual_ira_book():
    data = synthetic().model_dump(mode="json")
    data["ira_plan"] = None
    with pytest.raises(ValueError, match="require the household ordinary IRA"):
        project(Scenario.model_validate(data))
