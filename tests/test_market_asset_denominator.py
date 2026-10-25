"""Precision adjustments preserve other cash, every account and invested-HSA marks."""

from decimal import Decimal

import pytest

from wealthlab.household.calendar import money
from wealthlab.markets.household_exposure import gross_assets
from wealthlab.portfolio.household_book import Ledger
from wealthlab.portfolio.household_example import synthetic
from wealthlab.retirement.hsa_invested_example import synthetic as hsa_example
from wealthlab.retirement.hsa_invested_household import Investments


@pytest.mark.parametrize("price", ["100.004", "100.006", ".004"])
def test_denominator_uses_raw_positions_plus_actual_cash_without_a_weight_clamp(price):
    ledger = Ledger(synthetic())
    original = next(iter(ledger.book.lots.values()))
    ledger.book.lots = {original.id: original.model_copy(update=dict(quantity=Decimal(1)))}
    ledger.book.cash = {original.account_id: Decimal(7)}
    ledger.prices[original.security_id] = Decimal(price)
    row = dict(
        account_balances={original.account_id: money(Decimal(price) + 7), "reserve": Decimal(50)}
    )
    # Exposure precision must not alter spendable cash or the cent-settled wallet.
    before = dict(row["account_balances"])
    assert gross_assets(ledger, row) == Decimal(price) + 57
    assert row["account_balances"] == before
    assert ledger.book.cash[original.account_id] == 7


def test_rounding_is_account_local_even_when_two_accounts_hold_the_same_issuer():
    ledger = Ledger(synthetic())
    original = next(iter(ledger.book.lots.values()))
    ledger.book.lots = {
        "first": original.model_copy(update=dict(id="first", quantity=Decimal(1))),
        "second": original.model_copy(
            update=dict(id="second", account_id="second", quantity=Decimal(1))
        ),
    }
    ledger.book.cash = {original.account_id: Decimal(0), "second": Decimal(0)}
    ledger.prices[original.security_id] = Decimal("100.004")
    row = dict(account_balances={original.account_id: Decimal(100), "second": Decimal(100)})
    # Rounding each account to cents loses .004 twice, even for the same issuer.
    assert gross_assets(ledger, row) == Decimal("200.008")


def test_invested_hsa_exposes_same_raw_mark_bridge_without_changing_its_wallet_value():
    investments = Investments(hsa_example().hsa_plan.investments)
    investments.ledger.prices["fund"] = Decimal("100.00004")
    summary = investments.summary()
    assert summary["hsa_investment_mark_rounding"] == Decimal(".004")
    row = dict(account_balances={"hsa": Decimal(10100), "cash": Decimal(50)}, **summary)
    assert gross_assets(None, row) == Decimal("10150.004")
