"""A chronological invested-HSA book built on the existing lot/fee/distribution engine.

Only supplied prices at or before an event can fund a cash target. A target
raises cash inside the HSA; no external cash or recipient tax is invented.
Custodian fees retain their own unpaid liability and payment priority.
"""

from wealthlab.portfolio.book import Book
from wealthlab.portfolio.household_inputs import HouseholdMarks
from wealthlab.portfolio.timeline import events, handlers
from wealthlab.retirement.hsa_investment_funding import fund
from wealthlab.retirement.hsa_investment_reporting import snapshot
from wealthlab.retirement.hsa_investment_validation import validate


class Ledger:
    def __init__(self, plan):
        validate(plan)
        self.plan, self.book = plan, Book(plan.case)
        self.book.allocated_ids.update(r.id for r in [*plan.cash_targets, *plan.liquidity_locks])
        self.prices = dict(plan.opening_prices)
        self.when = plan.case.as_of
        self.cursor, self.counter = 0, 0
        self.generated, self.targets = [], []
        self.actions = handlers(plan.case, self.book, [])
        quotes = [*plan.marks, closing_quote(plan)]
        self.events = sorted(
            [
                *events(plan.case),
                *((m.date, -1, i, m) for i, m in enumerate(quotes)),
                *((t.date, 7, i, t) for i, t in enumerate(plan.cash_targets)),
            ],
            key=lambda row: row[:3],
        )

    def advance(self, when):
        if not self.when <= when <= self.plan.case.end:
            raise ValueError("HSA investment time must advance within the declared horizon.")
        while self.cursor < len(self.events) and self.events[self.cursor][0] <= when:
            date, kind, _, item = self.events[self.cursor]
            self.when = date
            self.apply(kind, item)
            self.cursor += 1
        self.when = when

    def apply(self, kind, item):
        if kind == -1:
            self.prices = dict(item.prices)
        elif kind == 7:
            available = fund(self, item.account_id, item.amount, item.date)
            self.targets.append(
                dict(
                    id=item.id,
                    date=item.date,
                    account_id=item.account_id,
                    requested=item.amount,
                    available=available,
                    unfilled=item.amount - available,
                )
            )
        else:
            if kind == 4 and item.action == "sell" and self.locked(item.security_id, item.date):
                raise ValueError("An entered HSA execution contradicts a supplied security lock.")
            self.actions[kind](item)

    def locked(self, security, when):
        return any(
            lock.security_id == security and lock.start <= when < lock.end
            for lock in self.plan.liquidity_locks
        )

    def raise_cash(self, account, requested, when):
        if account not in self.book.cash or requested < 0:
            raise ValueError("Cash requests require a known HSA and a nonnegative amount.")
        self.advance(when)
        return fund(self, account, requested, when)


def closing_quote(plan):
    return HouseholdMarks(date=plan.case.end, prices=plan.case.closing_prices)


def run(plan):
    ledger = Ledger(plan)
    ledger.advance(plan.case.end)
    return snapshot(ledger)
