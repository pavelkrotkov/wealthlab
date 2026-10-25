"""Qualification precedes liquidation, and unpaid provider seeds never become receipts."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_invested_example import synthetic


def test_ineligible_provider_election_cannot_sell_assets_or_create_receipts():
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"]["medical_bills"][0]["eligibility"] = "not_qualified"
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["hsa_audit"]
    assert not audit["investments"]["executed_trades"]
    assert rows[0]["medical_provider_paid"] == 0
    assert audit["receipt_remaining"]["care"] == 1000
    assert rows[-1]["medical_owed"] == 5000


def test_locked_assets_leave_actual_bill_owed_without_phantom_receipt_capacity():
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"]["investments"]["liquidity_locks"] = [
        dict(
            id="lock",
            provenance="assumption",
            security_id="fund",
            start="2026-01-01",
            end="2027-01-01",
        )
    ]
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["hsa_audit"]
    assert rows[0]["medical_provider_paid"] == 200
    assert rows[0]["medical_cash_paid"] == 1000
    assert rows[-1]["medical_owed"] == 4800
    assert audit["receipt_remaining"]["care"] == 1000
    assert not audit["investments"]["executed_trades"]


def test_unpaid_historical_claim_cannot_trigger_an_investment_sale():
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"]["medical_bills"] = []
    data["hsa_plan"]["withdrawals"] = [
        dict(
            id="unmatched",
            provenance="illustration",
            date="2026-01-09",
            source="hsa",
            amount=5000,
            mode="qualified_only",
            receipt_ids=[],
        )
    ]
    rows = project(Scenario.model_validate(data))
    assert not rows[-1]["hsa_audit"]["investments"]["executed_trades"]
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 0
