"""Saving instructions must refer to actual book assets and observed month-end prices."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.saving_example import synthetic


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("date", "2026-01-15", "month-end"),
        ("account_id", "missing", "known linked"),
        ("target_weights", {"stock": "0.5"}, "sum to one"),
        ("provenance", "unresolved", "Resolve"),
    ],
)
def test_unknown_or_unobserved_orders_do_not_buy_shares(field, value, message):
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["savings"][0][field] = value
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data))


def test_a_budget_smaller_than_its_commission_leaves_cash_untouched():
    data = synthetic().model_dump(mode="json")
    for saving in data["lot_plan"]["savings"]:
        saving["commission_per_trade"] = "501"
    rows = project(Scenario.model_validate(data))
    assert sum(r["saving_spent"] for r in rows) == 0
    assert sum(r["saving_commissions"] for r in rows) == 0
    assert rows[-1]["closing_cash"] == 2000
    assert rows[-1]["account_balances"]["brokerage"] == 0
