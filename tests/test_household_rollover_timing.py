"""Source receipt dates determine IRA principal availability without retroactive funding."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_rollover_example import synthetic


def test_transfer_does_not_backfill_an_earlier_unfilled_ira_draw():
    data = synthetic().model_dump(mode="json")
    data["ira_plan"]["orders"][0]["date"] = "2026-01-01"
    rows = project(Scenario.model_validate(data))
    assert rows[0]["ira_withdrawal_cash"] == 10000
    assert rows[0]["ira_unfilled_requests"] == 5000
    assert rows[1]["account_balances"]["ira"] == 80000
    assert rows[-1]["account_balances"]["ira"] == 80000


def test_same_day_transfer_is_available_to_the_ira_draw():
    data = synthetic().model_dump(mode="json")
    data["ira_plan"]["orders"][0]["date"] = "2026-02-01"
    rows = project(Scenario.model_validate(data))
    assert rows[1]["ira_withdrawal_cash"] == 15000
    assert rows[1]["account_balances"] == dict(cash=25000, work_pretax=20000, ira=75000)
    assert rows[1]["net_wealth"] == 120000
