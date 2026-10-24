"""Synthetic December loss: later observations finalize tax, not earlier spending cash."""

from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import synthetic as lot_household


def synthetic():
    data = lot_household().model_dump(mode="json")
    data["name"] = "Synthetic December loss and January tax reconciliation"
    data["accounts"][0]["balance"] = "100000"
    data["expenses"] = []
    plan = data["lot_plan"]
    plan.update(year_end_wash_policy="january_reconcile", funding_sources=[])
    plan["case"]["trades"] = [
        dict(
            id="december_loss",
            provenance="illustration",
            date="2026-12-20",
            action="sell",
            account_id="brokerage",
            security_id="stock",
            quantity="10",
            price="50",
            commission="0",
            selection="hifo",
        )
    ]
    return Scenario.model_validate(data)
