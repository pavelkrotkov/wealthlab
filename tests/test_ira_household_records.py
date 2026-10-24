"""Tax duplication, hidden IRA accounts and out-of-horizon schedules are rejected."""

from datetime import date
from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.household.storage import loads
from wealthlab.retirement.ira_household_example import synthetic


@pytest.mark.parametrize(
    "change,match",
    [
        (dict(products={"retirement": "traditional_ira"}), "every household"),
        (dict(returns=[], orders=[]), None),
    ],
)
def test_explicit_account_products_and_empty_schedules(change, match):
    c = synthetic()
    changed = c.model_copy(update=dict(ira_plan=c.ira_plan.model_copy(update=change)))
    if match:
        with pytest.raises(ValueError, match=match):
            project(changed)
    else:
        assert sum(r["ira_withdrawal_cash"] for r in project(changed)) == 0


def test_manual_ira_tax_cannot_duplicate_generated_recognition():
    c = synthetic()
    payload = c.model_dump(mode="json")
    payload["tax_plan"]["cases"][0]["federal_income"]["ira_distributions"] = "100"
    with pytest.raises(ValueError, match="manual IRA income"):
        project(Scenario.model_validate(payload))


def test_outside_horizon_event_cannot_disappear_silently():
    c = synthetic()
    order = c.ira_plan.orders[0].model_copy(update=dict(date=date(2030, 1, 1)))
    plan = c.ira_plan.model_copy(update=dict(orders=[order]))
    with pytest.raises(ValueError, match="inside the household"):
        project(c.model_copy(update=dict(ira_plan=plan)))


def test_original_history_is_immutable_and_serializable():
    c = synthetic()
    before = c.model_dump_json()
    result = project(c)
    assert c.model_dump_json() == before
    assert project(loads(before)) == result
    assert c.ira_plan.owners[0].roth_first_year is None
    assert result[-1]["account_balances"]["roth"] == Decimal(10000)
