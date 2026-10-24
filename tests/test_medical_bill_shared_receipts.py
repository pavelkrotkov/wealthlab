"""Actual cash-paid medical capacity is global across both owners and calendar years."""

from medical_bill_cases import data

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_two_owners_cannot_reuse_cash_paid_bill_capacity():
    value = data(cash=6000, hsa_amount=0, hsa_source=None, eligible_owners=["person_a", "person_b"])
    value["accounts"].append(
        dict(
            id="spouse_hsa",
            provenance="assumption",
            owner="person_b",
            wrapper="hsa",
            currency="USD",
            balance=3000,
            monthly_fee=0,
        )
    )
    plan = value["hsa_plan"]
    for year in plan["years"]:
        year["owners"][1]["established"] = "2020-01-01"
    plan["withdrawals"] = [
        dict(
            id=key,
            provenance="assumption",
            date=when,
            source=source,
            amount=amount,
            mode="qualified_only",
            receipt_ids=["care"],
        )
        for key, when, source, amount in (
            ("primary", "2026-03-01", "cash_hsa", 4000),
            ("spouse", "2026-03-01", "spouse_hsa", 4000),
            ("repeat", "2027-03-01", "cash_hsa", 1000),
        )
    ]
    plan["contributions"] = [
        dict(
            id="later_funding",
            provenance="assumption",
            date="2027-02-01",
            destination="cash_hsa",
            source="direct_employer",
            amount=1000,
        )
    ]
    rows = project(Scenario.model_validate(value))
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 6000
    assert rows[-1]["hsa_audit"]["receipt_remaining"] == {"care": 0}
    assert rows[14]["hsa_unfilled_requests"] == 1000
    assert rows[-1]["account_balances"]["cash_hsa"] == 1000
    assert rows[-1]["net_wealth"] == 12000 + 1000 - 6000
