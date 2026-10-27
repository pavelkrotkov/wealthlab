"""A completed share liquidation ends its request; only a blocked exit remains pending.

Subsequent funded capital follows its own explicit cash policy. Current-month
exit proceeds must retain exit character even when the pending state clears.
"""

from drilling_cases import change, short

from wealthlab.household.calendar import months
from wealthlab.household.funding import Wallet
from wealthlab.products.drilling_household import Ledger


def test_new_capital_after_completed_sale_is_retained_until_requested_partial_cash():
    def edit(data):
        plan = data["drilling_plan"]
        plan["mode"] = "liquid_reference"
        first, second, last = plan["observations"]
        first.update(exit_requested=True, reference_cash_request="0")
        second.update(capital_call="10000", reference_cash_request="0")
        last.update(exit_requested=False, reference_cash_request="2500")

    case = change(short(3), edit)
    ledger, wallet = Ledger(case), Wallet(case)
    first, second, last = months(case.start, case.end)
    ledger.after_receipts(wallet, *first)
    assert (ledger.reference_exit_pending, ledger.log[-1]["exit_cash"]) == (False, 100000)
    ledger.after_receipts(wallet, *second)
    assert (ledger.log[-1]["account_value"], ledger.log[-1]["exit_cash"]) == (10000, 0)
    ledger.after_receipts(wallet, *last)
    row = ledger.log[-1]
    assert (row["account_value"], row["distribution"], row["exit_cash"], wallet.cash) == (
        7500,
        2500,
        0,
        192500,
    )
    assert len(ledger.reference_book.disposals) == 2


def test_locked_pending_exit_survives_then_reports_one_exit_receipt_when_unlocked():
    def edit(data):
        plan = data["drilling_plan"]
        plan["mode"] = "liquid_reference"
        first, last = plan["observations"]
        first.update(exit_requested=True, reference_locked=True, reference_cash_request="0")
        last.update(exit_requested=False, reference_cash_request="0")

    case = change(short(2), edit)
    ledger, wallet = Ledger(case), Wallet(case)
    first, last = months(case.start, case.end)
    ledger.after_receipts(wallet, *first)
    assert (ledger.reference_exit_pending, ledger.log[-1]["blocked_exit"]) == (True, True)
    ledger.after_receipts(wallet, *last)
    row = ledger.log[-1]
    assert (ledger.reference_exit_pending, row["exit_cash"], row["distribution"]) == (
        False,
        100000,
        0,
    )
    assert (row["account_value"], wallet.cash) == (0, 200000)
