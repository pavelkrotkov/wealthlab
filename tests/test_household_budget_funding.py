"""Mandatory later sales retain funding priority after the estimated budget is consumed."""

from decimal import Decimal

from tests.household_budget_cases import synthetic
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_required_spending_sales_are_permitted_after_estimated_budget_is_consumed():
    data = synthetic().model_dump(mode="json")
    data["expenses"] = [
        dict(
            id="essential",
            provenance="illustration",
            start="2026-01-01",
            end="2027-01-01",
            monthly_amount="750",
            currency="USD",
            annual_growth=0,
            category="essential",
        )
    ]
    rows = project(Scenario.model_validate(data))
    final = rows[-1]
    audit = final["lot_audit"]["budget_audit"][0]
    spending, failed, sold = observed_funding(rows)
    assert spending == 9000
    assert not failed
    assert sold > 0
    assert audit["estimated_delta_at_decision"] == 500
    assert audit["estimate_after_observed_trades"] > 500
    assert not audit["estimated_budget_met_after_observed_trades"]
    # $11k opening wealth -$9k actual spending; microshare cent rounding is bounded.
    assert abs(final["net_wealth"] - Decimal(2000)) <= Decimal(".02")


def observed_funding(rows):
    return (
        sum(row["essential"] for row in rows),
        any(row["funding_failure"] for row in rows),
        sum(row["lot_funding_proceeds"] for row in rows),
    )
