"""Earlier policy receipts can fund later policies regardless of account listing order.

Two separately owned ledgers share one wallet and one return. The borrower starts
with $10,000 equity and receives $1,000 cash; paying the other policy's premium
must leave cash zero and combined net surrender wealth $20,800, not $21,800.
"""

from copy import deepcopy

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_household_example import event, synthetic


def two_policies():
    data = synthetic().model_dump(mode="json")
    data["end"] = "2026-02-01"
    data["accounts"][0]["balance"] = "0"
    data["expenses"][0]["monthly_amount"] = "0"
    borrower = data["life_plan"]["holdings"][0]
    recipient = deepcopy(borrower)
    recipient["account_id"] = "recipient"
    recipient["contract"]["events"] = [event("premium1", "2026-01-15", "premium", 1000)]
    recipient["failure_exits"].pop("premium2")
    borrower["contract"]["events"] = [
        event("loan", "2026-01-10", "loan_advance", 1000, cash_value_before="10000")
    ]
    borrower["failure_exits"] = {}
    data["life_plan"]["holdings"] = [recipient, borrower]
    data["accounts"].append(dict(data["accounts"][1], id="recipient"))
    return Scenario.model_validate(data)


def test_dated_receipts_are_yielded_before_a_later_policy_payment():
    row = project(two_policies())[0]
    audit = row["life_policy_audit"]["executed"]
    assert [e["kind"] for e in audit] == ["loan_advance", "premium"]
    assert row["life_payment_unfunded"] == 0
    assert row["closing_cash"] == 0
    assert row["net_wealth"] == 20800
    assert row["life_net_death_benefit"] == 199000
    assert row["life_protection_shortfall"] == 0
