"""Observed January facts and terminal no-replacement assumptions never create cash."""

import pytest

from tests.household_budget_cases import synthetic, two_year
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def year_end_loss(data, post="unconfirmed"):
    plan = data["lot_plan"]
    plan.update(year_end_wash_policy="january_reconcile", post_horizon_purchases=post)
    plan["case"]["lots"][0].update(federal_basis="15000", nj_basis="15000")
    first = plan["case"]["sale_policies"][0]
    plan["case"]["sale_policies"] = [dict(first, date="2026-12-31", tax_budget="0")]
    return data


def test_terminal_assumption_is_explicit_and_does_not_receive_a_future_refund():
    # An asserted future no-purchase window finalizes information, while the
    # actual cash book still stops on December31 and receives no phantom refund.
    data = year_end_loss(synthetic().model_dump(mode="json"), "none_for_30_days")
    final = project(Scenario.model_validate(data))[-1]
    record = final["lot_audit"]["budget_audit"][0]
    assert record["terminal_wash_assumption_used"]
    assert (record["tax_information_observed_on"], record["cash_observed_through"]) == (
        "2027-01-31",
        "2026-12-31",
    )
    assert record["estimated_delta_at_decision"] == 0
    assert record["estimate_after_observed_trades"] == -660
    assert record["actual_net_cash_tax_paid"] == 0
    assert final["closing_cash"] == 11000


def test_unknown_terminal_wash_window_still_blocks_the_household_result():
    data = year_end_loss(synthetic().model_dump(mode="json"))
    with pytest.raises(ValueError, match="Unfinalized tax returns"):
        project(Scenario.model_validate(data))


def test_actual_january_replacement_defers_loss_without_a_terminal_assumption():
    # The replacement is observed inside the cash horizon: its added federal
    # basis defers the prior loss rather than assuming the window expired.
    data = year_end_loss(two_year().model_dump(mode="json"))
    data["lot_plan"]["case"]["trades"] = [
        dict(
            id="observed_replacement",
            provenance="illustration",
            date="2027-01-15",
            action="buy",
            account_id="brokerage",
            security_id="stock",
            quantity="100",
            price="100",
            commission="0",
        )
    ]
    final = project(Scenario.model_validate(data))[-1]
    record = final["lot_audit"]["budget_audit"][0]
    assert not record["terminal_wash_assumption_used"]
    assert record["estimated_delta_at_decision"] == record["estimate_after_observed_trades"] == 0
    assert record["actual_lot_long_term"] == 0
    assert final["lot_audit"]["disposals"][0]["federal_wash_deferred"] == 5000
    assert final["net_wealth"] == 11000
