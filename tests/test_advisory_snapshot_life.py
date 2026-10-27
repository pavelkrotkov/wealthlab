"""Actual opening policy loan debt is deducted before the stored life-value fee base."""

from decimal import Decimal

from tests.advisory_cases import change
from tests.advisory_snapshot_cases import snapshot_fee
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_household_example import synthetic


def test_opening_life_snapshot_uses_opening_loan_and_not_later_premium_values():
    data = synthetic().model_dump(mode="json")
    data["life_plan"]["holdings"][0]["contract"]["opening_loan"] = "500"
    data["accounts"][1]["balance"] = "9500"
    case = Scenario.model_validate(data)
    baseline = project(case)
    selected = snapshot_fee(case, account="life_policy", rate=".12")

    def life_basis(plan):
        plan["schedules"][0]["covered"][0]["value_basis"] = "life_net_cash_value"

    rows = project(change(selected, life_basis))
    assert rows[0]["advisory_fee_assessments"][0]["valuation_base"] == 9500
    assert rows[0]["advisory_fees_paid"] == 95
    snapshot = rows[-1]["advisory_fee_audit"]["observed_snapshots"][0]
    assert snapshot["life_values"][0]["loan"] == 500
    assert rows[-1]["net_wealth"] == baseline[-1]["net_wealth"] - Decimal(95)
