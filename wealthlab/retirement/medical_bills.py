"""Actual provider/cash payments create receipt capacity; unpaid bills remain owed.

This book owns net bill liabilities, not insurance claims or tax deductions.
HSA's existing qualified-expense and age-exception engine still classifies
actual distributions. Provider payments never become household cash income.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.retirement import hsa, hsa_receipts
from wealthlab.retirement.hsa_inputs import HSAWithdrawal

ZERO = Decimal(0)


class Bills:
    def __init__(self, bills):
        self.bills = {b.id: b for b in bills}
        self.remaining = {}
        self.hsa_paid = dict.fromkeys(self.bills, ZERO)
        self.log = []
        self.payments = []
        self.direct_paid = ZERO

    def initialize_receipts(self, book):
        # These are bill metadata, not previously paid receipts. Dynamic paid
        # capacity survives year boundaries through the existing shared book.
        for key in self.bills:
            book["receipt_remaining"][key] = ZERO

    def start(self, start, end):
        self.start_date, self.end = start, end
        self.direct_paid = ZERO
        self.payments = []

    def issue(self, bill):
        if bill.id in self.remaining:
            raise ValueError("A medical bill cannot be issued twice.")
        self.remaining[bill.id] = bill.amount

    def provider(self, book, bill, when):
        amount = self.provider_capacity(book, bill, when)
        if not amount:
            return
        owner = book["owners"][book["accounts"][bill.hsa_source].owner]
        receipt = book["receipts"][bill.id]
        qualified = hsa_receipts.available(receipt, owner, when, {bill.id: amount})
        book["receipt_remaining"][bill.id] += qualified
        order = HSAWithdrawal(
            id=bill.id,
            provenance=bill.provenance,
            date=when,
            source=bill.hsa_source,
            amount=amount,
            mode=bill.hsa_mode,
            receipt_ids=[bill.id],
        )
        hsa.withdraw(book, order)
        row = book["rows"][-1]
        paid = row["funded"]
        book["cash"] -= paid
        row["cash_destination"] = "medical_provider"
        self.remaining[bill.id] -= paid
        self.hsa_paid[bill.id] += paid
        self.direct_paid += paid
        self.record(bill.id, when, "hsa_provider", paid)

    def provider_capacity(self, book, bill, when):
        if bill.hsa_source is None:
            return ZERO
        amount = min(
            self.remaining[bill.id],
            bill.hsa_amount - self.hsa_paid[bill.id],
            book["balances"][bill.hsa_source],
        )
        if bill.hsa_mode == "qualified_only":
            owner = book["owners"][book["accounts"][bill.hsa_source].owner]
            amount = hsa_receipts.available(
                book["receipts"][bill.id], owner, when, {bill.id: amount}
            )
        return amount

    def retry(self, book):
        # Earlier HSA events retain their actual chronology. A later deposit can
        # pay an outstanding bill on this month-end retry, never on an earlier date.
        for key in self.remaining:
            self.provider(book, self.bills[key], self.end - timedelta(days=1))

    @property
    def owed(self):
        return sum(self.remaining.values(), ZERO)

    def fund(self, wallet, book):
        cash = ZERO
        for key in sorted(self.remaining, key=lambda k: self.bills[k].date):
            paid = wallet.pay(self.remaining[key])
            self.remaining[key] -= paid
            book["receipt_remaining"][key] += paid
            cash += paid
            if paid:
                self.record(key, self.end - timedelta(days=1), "household_cash", paid)
        return dict(
            medical_provider_paid=self.direct_paid,
            medical_cash_paid=cash,
            medical_owed=self.owed,
            medical_bills_unfunded=self.new_unfunded(),
            medical_arrears_paid=self.arrears_paid(),
        )

    def new_unfunded(self):
        return sum(
            (
                value
                for key, value in self.remaining.items()
                if self.start_date <= self.bills[key].date < self.end
            ),
            ZERO,
        )

    def arrears_paid(self):
        return sum(
            (
                row["paid"]
                for row in self.payments
                if self.bills[row["bill"]].date < self.start_date
            ),
            ZERO,
        )

    def record(self, key, when, source, paid):
        row = dict(bill=key, date=when, source=source, paid=paid, remaining=self.remaining[key])
        self.payments.append(row)
        self.log.append(row)

    def audit(self):
        return dict(
            payments=self.log,
            remaining=dict(self.remaining),
            elections=[
                dict(
                    bill=b.id,
                    hsa_requested=b.hsa_amount,
                    hsa_paid=self.hsa_paid[b.id],
                    hsa_unfilled=b.hsa_amount - self.hsa_paid[b.id],
                )
                for b in self.bills.values()
            ],
        )
