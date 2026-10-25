"""Process HSA investments and recipient events in declared chronological order.

Investment events on a date precede recipient orders on that date. A month's
final retry can observe later deposits, prices and locks, never future months.
All cash changes return to the same persistent investment account.
"""

from datetime import timedelta

from wealthlab.retirement import hsa
from wealthlab.retirement.medical_bill_inputs import MedicalBill


def apply(ledger, start, end):
    investments, book = ledger.investments, ledger.book
    for when, _, _, item in ledger.events:
        if start <= when < end:
            if investments is not None:
                investments.advance(book, when)
            if isinstance(item, MedicalBill):
                ledger.medical.issue(item)
                ledger.medical.provider(book, item, when)
            else:
                hsa.apply(book, item)
            if investments is not None:
                investments.sync_cash(book)
    if investments is not None:
        investments.advance(book, end - timedelta(days=1))
    ledger.medical.retry(book)
