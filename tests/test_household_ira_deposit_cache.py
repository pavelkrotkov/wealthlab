"""Unchanged funded state must not repeat the complete annual reconciliation."""

from unittest.mock import patch

from wealthlab.household.projection import project
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_deposit_household_example import synthetic


def test_annual_work_scales_with_funded_changes_instead_of_calendar_months():
    case = synthetic()
    with patch("wealthlab.retirement.ira_household_dynamic.run", wraps=run) as reconcile:
        rows = project(case)
    # Two opening annual books and four actual funded deposits need at most six runs.
    assert reconcile.call_count <= 6
    assert rows[-1]["net_wealth"] == 154086


def test_unfunded_requests_remain_auditable_without_repeating_annual_work():
    from tests.ira_deposit_household_cases import one_year
    from wealthlab.household.scenario import Scenario

    data = one_year().model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["incomes"] = []
    data["tax_plan"]["income_rules"] = []
    plan = data["ira_plan"]
    plan["orders"] = []
    order = plan["contributions"]["orders"][0]
    plan["contributions"]["orders"] = [
        dict(order, id=f"unfunded_{month}", date=f"2026-{month:02}-01") for month in range(1, 13)
    ]
    with patch("wealthlab.retirement.ira_household_dynamic.run", wraps=run) as reconcile:
        rows = project(Scenario.model_validate(data))
    assert reconcile.call_count == 1
    assert len(rows[-1]["ira_contribution_audit"]) == 12
    assert sum(r["ira_contributions_unfilled"] for r in rows) == 36000
