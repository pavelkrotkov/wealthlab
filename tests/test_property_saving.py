"""Closing debt disappears from the shared required-cash quote before optional share purchases."""

from tests.property_cases import change
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import plan


def test_actual_payoff_releases_only_the_real_remaining_surplus_for_optional_saving():
    def changed(data):
        data["accounts"].append(
            dict(
                id="brokerage",
                provenance="illustration",
                owner="person_a",
                currency="USD",
                wrapper="taxable",
                balance="0",
                monthly_fee="0",
            )
        )
        lots = plan(Scenario.model_validate(data))
        lots["case"]["lots"] = []
        lots["case"]["closing_prices"] = dict(stock="100")
        lots["funding_sources"] = []
        lots["savings"] = [
            dict(
                id="save_close_surplus",
                provenance="illustration",
                date="2026-06-30",
                account_id="brokerage",
                amount="300000",
                target_weights=dict(stock="1"),
                commission_per_trade="0",
                minimum_cash="0",
            )
        ]
        data["lot_plan"] = lots

    rows = project(change(changed))
    assert rows[5]["saving_spent"] == 246400
    assert rows[5]["saving_unfilled"] == 53600
    assert rows[5]["debt_payment"] == rows[5]["closing_cash"] == 0
    assert rows[-1]["net_wealth"] == rows[-1]["account_balances"]["brokerage"] == 246400
    assert rows[-1]["lot_audit"]["disposals"] == []
