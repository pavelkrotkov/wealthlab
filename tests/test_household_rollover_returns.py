"""Source and destination earn their own remaining month-end returns after the transfer."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_rollover_example import synthetic


def test_month_end_returns_apply_only_to_each_accounts_actual_remaining_principal():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["returns"] = [
        dict(
            id="source_gain",
            provenance="illustration",
            date="2026-02-28",
            account_id="work_pretax",
            rate=".10",
        )
    ]
    data["ira_plan"]["returns"] = [
        dict(
            id="ira_gain",
            provenance="illustration",
            date="2026-02-28",
            account_id="ira",
            rate=".10",
        )
    ]
    rows = project(Scenario.model_validate(data))
    assert rows[1]["workplace_market_change"] == 2000
    assert rows[1]["account_balances"]["ira"] == 99000
    assert rows[2]["account_balances"] == dict(cash=25000, work_pretax=22000, ira=84000)
    assert rows[2]["net_wealth"] == 131000
