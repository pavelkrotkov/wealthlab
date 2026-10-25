"""Intent, target coverage and schedule validation happen before any trade."""

import pytest
from rebalance_cases import payload

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


@pytest.mark.parametrize(
    "edit,match",
    [
        (dict(provenance="unresolved"), "Resolve rebalance"),
        (dict(date="2026-01-30"), "month-end"),
        (dict(date="2025-12-31"), "horizon"),
        (dict(account_id="unknown"), "known linked"),
        (dict(target_weights=dict(stock=".5", unknown=".5")), "known linked"),
        (dict(target_weights=dict(stock=".4", bond=".5")), "sum exactly"),
        (dict(target_weights=dict(bond="1")), "every account holding"),
        (dict(id="low_basis"), "IDs must be unique"),
    ],
)
def test_bad_decision_inputs_cannot_reach_wallet(edit, match):
    data = payload()
    data["lot_plan"]["rebalances"][0].update(edit)
    with pytest.raises(ValueError, match=match):
        project(Scenario.model_validate(data))


@pytest.mark.parametrize("duplicate_id", [True, False])
def test_duplicate_dates_or_ids_do_not_churn_holdings(duplicate_id):
    data = payload()
    policy = data["lot_plan"]["rebalances"][0]
    data["lot_plan"]["rebalances"].append(
        dict(policy, id=policy["id"] if duplicate_id else "other")
    )
    with pytest.raises(ValueError, match=r"unique|once per account"):
        project(Scenario.model_validate(data))
