"""Scheduled saving transfers real cash once and must stop before a complete-exit ranking.

With flat fully based shares, an early purchase changes asset location but not
ending wealth. A purchase after the final sale deliberately reopens the book;
that case must retain marked wealth and lose after-tax-exit eligibility.
"""

from decimal import Decimal

import pytest
from optimization_cases import flat

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search


def saving_case(when):
    data = flat().model_dump(mode="json")
    data["household"]["lot_plan"]["savings"] = [
        dict(
            id="scheduled_saving",
            provenance="illustration",
            date=when,
            account_id="brokerage",
            amount="1000",
            target_weights=dict(stock="1"),
            commission_per_trade="0",
            minimum_cash="0",
        )
    ]
    return PolicySearch.model_validate(data)


@pytest.fixture(scope="module")
def early():
    return search(saving_case("2026-01-31"))


def test_early_saving_preserves_fully_liquidated_household_capital(early):
    assert early["candidates"][0]["median_real_after_tax_exit_wealth"] == 251999
    rows = early["selected_training"]["details"][0]["rows"]
    assert rows[0]["saving_spent"] == 1000
    assert rows[-1]["account_balances"]["brokerage"] == 0


def test_new_shares_have_real_cash_cost_and_survive_to_the_actual_exit(early):
    audit = early["selected_training"]["details"][0]["rows"][-1]["lot_audit"]
    buys = [t for t in audit["trades"] if t["action"] == "buy"]
    assert len(buys) == 1
    assert Decimal(buys[0]["quantity"]) == 10


def test_saving_after_exit_cannot_reuse_a_completed_liquidation_label():
    result = search(saving_case("2027-12-31"))
    assert result["selection"] is None
    assert all(not c["constraints"]["completed_after_tax_exit"] for c in result["candidates"])
