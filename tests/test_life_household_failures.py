"""A missed premium terminates only under the explicitly supplied failure settlement.

The unpaid $1,000 premium remains a funding failure, while the $10,000 surrender
receipt can meet ordinary household spending. Future illustrated values and loan
receipts disappear; neither the missed premium nor lost death protection is cash.
"""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_household_example import synthetic


def test_unaffordable_premium_uses_supplied_exit_and_cancels_later_policy_values():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "600"
    rows = project(Scenario.model_validate(data))
    assert rows[0]["life_payment_unfunded"] == 1000
    assert rows[0]["funding_failure"]
    assert rows[-1]["closing_cash"] == 7600
    assert rows[-1]["net_wealth"] == 7600
    assert rows[-1]["account_balances"]["life_policy"] == 0
    audit = rows[-1]["life_policy_audit"]
    assert [r["event"] for r in audit["cancelled"]] == ["premium2", "loan"]


def test_failed_policy_payment_is_not_annualized_into_future_cash_reserves():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "600"
    rows = project(Scenario.model_validate(data))
    assert [r["reserve_target"] for r in rows] == [24000, 24000, 24000]
    assert all(r["life_reserve_target"] == 0 for r in rows)
    assert all(r["life_net_death_benefit"] == 0 for r in rows)
    assert all(r["life_protection_shortfall"] == 150000 for r in rows)
