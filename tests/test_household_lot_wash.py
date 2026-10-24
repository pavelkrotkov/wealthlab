"""Pending losses cannot become spending cash or migrate silently across tax years."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import synthetic


def loss_data(when="2026-06-15"):
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "100000"
    data["expenses"] = []
    data["lot_plan"]["funding_sources"] = []
    data["lot_plan"]["case"]["trades"] = [
        dict(
            id="manual_loss",
            provenance="illustration",
            date=when,
            action="sell",
            account_id="brokerage",
            security_id="stock",
            quantity="10",
            price="50",
            commission="0",
            selection="hifo",
        )
    ]
    return data


def test_loss_is_excluded_until_the_actual_forward_window_expires():
    rows = project(Scenario.model_validate(loss_data()))
    assert rows[5]["annual_tax"]["federal"]["agi"] == 30000
    assert rows[6]["annual_tax"]["federal"]["agi"] == 34600
    # The recognized NJ disposition loss cannot reduce the separate wage category.
    assert rows[5]["annual_tax"]["new_jersey"]["gross_income"] == 30000
    assert rows[-1]["lot_audit"]["disposals"][0]["nj_recognized_gain"] == -300
    assert sum(r["tax_event_cash"] for r in rows) == 0


def test_replacement_keeps_the_loss_out_of_income_and_adjusts_the_actual_new_lot():
    data = loss_data()
    data["lot_plan"]["case"]["trades"].append(
        dict(
            id="replacement",
            provenance="illustration",
            date="2026-07-15",
            action="buy",
            account_id="brokerage",
            security_id="stock",
            quantity="10",
            price="50",
            commission="0",
        )
    )
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["lot_audit"]
    assert audit["disposals"][0]["federal_wash_deferred"] == 400
    replacement = next(lot for lot in audit["lots"] if lot["id"] == "replacement")
    assert replacement["federal_basis"] == "900.00"
    assert rows[6]["annual_tax"]["federal"]["agi"] == 35000


def test_pending_december_loss_blocks_until_prior_return_adapter_exists():
    with pytest.raises(ValueError, match="January/prior-return reconciliation"):
        project(Scenario.model_validate(loss_data("2026-12-20")))
