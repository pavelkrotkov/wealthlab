"""January finalizes the original return while April supplies actual refund cash.

The earlier December payment is an actual modeled cash movement and cannot
be undone. January recognition creates a receivable only. An observed buy
instead defers the loss into replacement basis. At the terminal boundary,
unused capital carry is reported without inventing a refundable cash benefit.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.january_example import synthetic


def test_original_year_loss_creates_a_receivable_without_retroactive_cash():
    rows = project(synthetic())
    audit = rows[-1]["lot_audit"]["return_reconciliations"][0]
    assert rows[11]["tax_return_provisional"]
    assert audit["year"] == 2026
    assert audit["old_result"]["federal"]["agi"] == 60000
    assert audit["final_result"]["federal"]["agi"] == 59600
    assert rows[11]["closing_cash"] == rows[12]["closing_cash"]
    assert rows[12]["tax_refund_receivable"] == 48
    assert rows[15]["tax_refund_received"] == 48


def test_january_replacement_defers_the_loss_instead_of_claiming_a_refund():
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["case"]["trades"].append(
        dict(
            id="replacement",
            provenance="illustration",
            date="2027-01-10",
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
    assert audit["return_reconciliations"][0]["final_result"]["federal"]["agi"] == 60000
    assert sum(r["tax_refund_received"] for r in rows) == 0


def terminal_data():
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["case"]["trades"][0]["date"] = "2027-12-20"
    return data


def test_unobserved_terminal_window_needs_an_explicit_assumption():
    with pytest.raises(ValueError, match="January observations or a no-replacement"):
        project(Scenario.model_validate(terminal_data()))


def test_assumed_terminal_closure_creates_no_refund_cash_before_receipt():
    data = terminal_data()
    data["lot_plan"]["post_horizon_purchases"] = "none_for_30_days"
    rows = project(Scenario.model_validate(data))
    assert rows[-1]["terminal_wash_assumption"] == "no_replacements_30_days"
    assert not rows[-1]["tax_return_provisional"]
    assert sum(r["tax_refund_received"] for r in rows) == 0
    assert rows[-1]["annual_tax"]["federal"]["long_carry"] == Decimal("400")
