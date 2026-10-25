"""Actual shares, independent bases and cash must conserve capital after fees."""

from decimal import Decimal

import pytest
from rebalance_cases import book_case, payload

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.rebalance import decide


@pytest.fixture(scope="module")
def projected():
    return project(Scenario.model_validate(payload()))


def test_half_allocation_uses_independent_tax_bases(projected):
    sale = projected[-1]["lot_audit"]["disposals"][0]
    assert sale["federal_gross_gain"] == 450
    assert sale["nj_gross_gain"] == 400


def test_actual_shares_and_household_capital_are_conserved(projected):
    audit = projected[-1]["lot_audit"]
    assert {lot["security_id"]: Decimal(lot["quantity"]) for lot in audit["lots"]} == {
        "stock": 5,
        "bond": 5,
    }
    assert projected[-1]["net_wealth"] == 2000
    assert audit["rebalance_decisions"][0]["residual_cash"] == 0


def test_two_commissions_reduce_wealth_once_and_enter_purchase_basis():
    book, policy, prices = book_case(commission_per_trade="1")
    result = decide(book, policy, prices, set())
    bond = next(lot for lot in book.lots.values() if lot.security_id == "bond")
    assert bond.quantity == Decimal("4.98")
    assert bond.federal_basis == bond.nj_basis == 499
    assert (
        result["commissions"],
        result["gross_sales"],
        result["gross_purchases"],
        result["residual_cash"],
    ) == (2, 500, 498, 0)
