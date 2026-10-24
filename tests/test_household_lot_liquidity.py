"""Positive wealth cannot pay a bill when shares are locked or sales forbidden.

Funding permission and dated liquidity are separate from mark value. A HIFO
preference cannot sell a locked lot ahead of an eligible one, and an optional
manual purchase cannot borrow against later wages. Missed obligations must
remain visible even when the household still owns substantial marked assets.
"""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import synthetic


def test_illiquid_shares_leave_visible_spending_and_tax_gaps():
    data = synthetic().model_dump(mode="json")
    for lot in data["lot_plan"]["case"]["lots"]:
        lot["liquid_after"] = "2040-01-01"
    rows = project(Scenario.model_validate(data))
    assert sum(r["funding_sale_proceeds"] for r in rows) == 0
    assert sum(r["funding_shortfall"] for r in rows) > 0
    assert rows[-1]["net_wealth"] > 0
    assert rows[-1]["funding_failure"]
    assert all(r["closing_cash"] >= 0 for r in rows)


def test_absent_sale_permission_does_not_imply_liquidation():
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["funding_sources"] = []
    rows = project(Scenario.model_validate(data))
    assert sum(r["lot_funding_proceeds"] for r in rows) == 0
    assert any(r["funding_failure"] for r in rows)
    assert not rows[-1]["lot_audit"]["funding_orders"]


def test_locked_high_basis_shares_do_not_override_available_low_basis_shares():
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["case"]["lots"][1]["liquid_after"] = "2027-01-01"
    rows = project(Scenario.model_validate(data))
    disposals = rows[-1]["lot_audit"]["disposals"]
    first_year = [r for r in disposals if r["date"].startswith("2026")]
    assert first_year
    assert {r["lot_id"] for r in first_year} == {"low_basis"}


def test_a_manual_purchase_cannot_spend_later_months_wages():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["lot_plan"]["case"]["trades"] = [
        dict(
            id="unfunded_buy",
            provenance="illustration",
            date="2026-01-15",
            action="buy",
            account_id="brokerage",
            security_id="stock",
            quantity="100",
            price="100",
            commission="0",
        )
    ]
    with pytest.raises(ValueError, match="cannot borrow or use future receipts"):
        project(Scenario.model_validate(data))
