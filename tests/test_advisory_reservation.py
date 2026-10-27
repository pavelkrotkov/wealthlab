"""Scoped encumbrance never moves funds; required funding uses gross cash and the full quote."""

from datetime import date
from decimal import Decimal

from tests.advisory_cases import native
from wealthlab.household.funding import Wallet
from wealthlab.portfolio.household_book import make
from wealthlab.tax.projection_ledger import TaxLedger

START, END = date(2026, 1, 1), date(2026, 2, 1)


def test_required_native_sale_compares_gross_cash_to_full_fee_plus_medical_or_tuition_quote():
    case, _, _ = native(cash="0")
    wallet, lots = Wallet(case), make(case)
    ledger = TaxLedger(case.tax_plan, case, lots)

    def required_wrapper(wallet, start, end):
        with wallet.reserving(Decimal(100)):
            ledger.fund_required(wallet, Decimal(100), start, end)
            # Gross $200 contains $100 reserved fee plus $100 actual required payment.
            assert wallet.balances["cash"] == 200
            assert wallet.cash == 100
            assert wallet.pay(Decimal(100)) == 100
            assert wallet.cash == 0
        return ()

    result = ledger.month(
        {},
        wallet,
        START,
        END,
        Decimal(100),
        receipt_hook=required_wrapper,
        pre_receipt_hook=lots.after_receipts,
    )
    assert result["funding_sale_proceeds"] == 200
    assert wallet.cash == 100
    assert wallet.reserved_cash == 0
    assert lots.book.disposals[0]["proceeds"] == 200


def test_later_actual_receipt_reduces_the_same_reserved_funding_sale_without_double_quote():
    case, _, _ = native(cash="0")
    wallet, lots = Wallet(case), make(case)
    ledger = TaxLedger(case.tax_plan, case, lots)

    def required_wrapper(wallet, start, end):
        with wallet.reserving(Decimal(100)):
            wallet.deposit(Decimal(150))
            ledger.fund_required(wallet, Decimal(100), start, end)
            assert wallet.pay(Decimal(100)) == 100
        return ()

    result = ledger.month(
        {},
        wallet,
        START,
        END,
        Decimal(100),
        receipt_hook=required_wrapper,
        pre_receipt_hook=lots.after_receipts,
    )
    assert result["funding_sale_proceeds"] == 50
    assert wallet.cash == 100
    assert lots.book.disposals[0]["proceeds"] == 50
