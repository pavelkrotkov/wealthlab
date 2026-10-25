"""Optional saving sees the new fee in the shared quote and cannot borrow or spend its cash."""

from tests.advisory_cases import native, with_fee
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_saving_only_profile_retains_the_bill_before_buying_new_shares():
    case, _, _ = native(cash="1000")
    data = case.model_dump(mode="json")
    data["accounts"][1]["balance"] = "0"
    data["lot_plan"]["case"]["lots"] = []
    data["lot_plan"]["funding_sources"] = []
    data["lot_plan"]["savings"] = [
        dict(
            id="invest_surplus",
            provenance="illustration",
            date="2026-01-31",
            account_id="brokerage",
            amount="1000",
            target_weights=dict(stock="1"),
            commission_per_trade="0",
            minimum_cash="0",
        )
    ]
    rows = project(with_fee(Scenario.model_validate(data), account="cash", rate=".12"))
    assert rows[0]["saving_spent"] == 990
    assert rows[0]["saving_unfilled"] == 10
    assert rows[0]["advisory_fees_paid"] == 10
    assert rows[0]["closing_cash"] == 0
    assert rows[-1]["net_wealth"] == rows[-1]["account_balances"]["brokerage"] == 990
    assert rows[-1]["lot_audit"]["disposals"] == []
