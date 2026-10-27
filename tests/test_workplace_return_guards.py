"""Monthly payroll timing requires month-end return events and explicit known products."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_example import synthetic


@pytest.mark.parametrize(
    "changes",
    [dict(date="2026-01-15"), dict(account_id="cash"), dict(provenance="unresolved")],
)
def test_invalid_manual_workplace_returns_block(changes):
    data = synthetic().model_dump(mode="json")
    event = dict(
        id="return",
        provenance="assumption",
        date="2026-01-31",
        account_id="work_pretax",
        rate=".1",
    )
    data["workplace_plan"]["returns"] = [dict(event, **changes)]
    with pytest.raises(ValueError):
        project(Scenario.model_validate(data))
