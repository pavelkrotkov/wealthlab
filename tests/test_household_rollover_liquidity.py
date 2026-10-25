"""Optional transfers use only actual unlocked source principal and are never retried."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_rollover_example import synthetic


def test_insufficient_plan_value_funds_only_the_actual_balance():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["direct_rollovers"][0]["amount"] = 150000
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["workplace_rollover_audit"][0]
    assert (audit["funded"], audit["unfilled"]) == (100000, 50000)
    assert rows[1]["account_balances"] == dict(cash=10000, work_pretax=0, ira=110000)
    assert rows[1]["net_wealth"] == 120000


def test_a_later_unlocked_source_does_not_retry_the_failed_request():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["liquidity_locks"] = [
        dict(
            id="transfer_lock",
            provenance="illustration",
            account_id="work_pretax",
            start="2026-02-01",
            end="2026-03-01",
        )
    ]
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["workplace_rollover_audit"]
    assert len(audit) == 1
    assert audit[0]["blocked_by_liquidity"]
    assert audit[0]["funded"] == 0
    assert rows[2]["ira_withdrawal_cash"] == 10000
    assert rows[2]["ira_unfilled_requests"] == 5000
    assert rows[-1]["account_balances"]["work_pretax"] == 100000
