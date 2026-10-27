"""Unfunded new-issue premiums execute supplied settlements without free coverage."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_allocation_example import synthetic


def cash_case(amount):
    data = synthetic().alternatives["new_issue"].model_dump(mode="json")
    data["accounts"][0]["balance"] = str(amount)
    data["expenses"][0]["monthly_amount"] = "0"
    return data


def test_first_premium_failure_never_creates_policy_asset_basis_loan_or_protection():
    rows = project(Scenario.model_validate(cash_case(500)))
    assert [
        (r["closing_cash"], r["life_net_death_benefit"], r["life_protection_shortfall"])
        for r in rows
    ] == [(500, 0, 150000)] * 3
    assert rows[0]["life_payment_unfunded"] == 1000
    audit = rows[-1]["life_policy_audit"]
    first = audit["executed"][0]
    assert (first["failure_exit"], first["closed"]) == (True, True)
    assert first["federal_basis_after"] == first["loan_after"] == first["received_cash"] == 0
    assert [r["event"] for r in audit["cancelled"]] == ["new_premium2", "new_surrender"]


def test_later_premium_failure_preserves_actual_sunk_cost_and_cancels_full_path():
    rows = project(Scenario.model_validate(cash_case(1500)))
    assert [r["closing_cash"] for r in rows] == [500, 1400, 1400]
    assert [r["life_net_death_benefit"] for r in rows] == [100000, 0, 0]
    assert rows[1]["life_payment_unfunded"] == 1000
    audit = rows[-1]["life_policy_audit"]
    assert [e["payment_paid"] for e in audit["executed"]] == [1000, 0]
    assert (
        audit["executed"][-1]["received_cash"],
        audit["executed"][-1]["federal_ordinary_income"],
    ) == (900, 0)
    assert [r["event"] for r in audit["cancelled"]] == ["new_surrender"]
