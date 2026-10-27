"""Unfunded reserves survive partial funding and exceptions without hidden borrowing.

A sale limit is a real constraint, not a reason to lend the missing fee cash.
The native solver still owns gains and cash; the temporary reservation only
protects an existing bill until optional wrapper execution has completed.
"""

from datetime import date
from decimal import Decimal

import pytest

from tests.advisory_cases import native
from wealthlab.household.funding import Wallet
from wealthlab.portfolio.household_book import make
from wealthlab.tax.projection_ledger import TaxLedger

START, END = date(2026, 1, 1), date(2026, 2, 1)


@pytest.mark.parametrize("locked, expected", [(True, 0), (False, 100)])
def test_partial_or_locked_native_sale_never_spends_the_same_fee_reserve_twice(locked, expected):
    case, _, _ = native(cash="0")
    lot = case.lot_plan.case.lots[0].model_copy(
        update=dict(quantity=Decimal(1), federal_basis=Decimal(20), nj_basis=Decimal(30))
    )
    book = case.lot_plan.case.model_copy(update=dict(lots=[lot]))
    account = case.accounts[1].model_copy(update=dict(balance=Decimal(100)))
    case = case.model_copy(
        update=dict(
            accounts=[case.accounts[0], account, *case.accounts[2:]],
            lot_plan=case.lot_plan.model_copy(update=dict(case=book)),
        )
    )
    wallet, lots = Wallet(case), make(case)
    lots.locked = {"stock"} if locked else set()
    ledger = TaxLedger(case.tax_plan, case, lots)

    def wrapper(wallet, start, end):
        with wallet.reserving(Decimal(100)):
            ledger.fund_required(wallet, Decimal(100), start, end)
            assert wallet.reserved_cash == 100
            assert wallet.pay(Decimal(100)) == 0
        return ()

    result = ledger.month(
        {},
        wallet,
        START,
        END,
        Decimal(100),
        receipt_hook=wrapper,
        pre_receipt_hook=lots.after_receipts,
    )
    assert result["funding_sale_proceeds"] == expected
    assert wallet.cash == expected
    assert wallet.reserved_cash == 0
