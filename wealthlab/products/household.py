"""Run ordered household sleeves using actual cash and separately supplied tax recognition.

The source plan remains immutable. Each mutable economic book persists across
months, including its debt, while the available cash comes from the current
household wallet rather than a separate synthetic investor reserve.
"""

from wealthlab.products.conditional_allocations import audit as tax_audit
from wealthlab.products.conditional_allocations import events as tax_events
from wealthlab.products.household_cash import execute
from wealthlab.products.household_reporting import summarize
from wealthlab.products.household_validation import validate
from wealthlab.products.long_short_book import opening
from wealthlab.products.private_fund_household import FundLedger
from wealthlab.products.sleeve_exit_state import record as record_exits


class Ledger:
    def __init__(self, scenario):
        validate(scenario)
        self.plan = scenario.sleeve_plan
        self.end = scenario.end
        self.books = {s.account_id: opening(s.case) for s in self.plan.sleeves}
        self.allocations = {
            s.account_id: [e for a in s.allocations for e in tax_events(a)]
            for s in self.plan.sleeves
        }
        self.funds = {
            s.account_id: FundLedger(s) for s in self.plan.sleeves if s.private_fund_contract
        }
        self.month = 0
        self.log = []
        self.summary = {}

    def after_receipts(self, wallet, start, end):
        audits, events = [], []
        for sleeve in self.plan.sleeves:
            if sleeve.account_id in self.funds:
                row, fund_events = self.funds[sleeve.account_id].execute(
                    self.month, wallet, start, end
                )
                audits.append(row)
                events.extend(fund_events)
            else:
                audits.append(
                    execute(self.books[sleeve.account_id], sleeve, self.month, wallet, end)
                )
            events.extend(a for a in self.allocations[sleeve.account_id] if start <= a.date < end)
        self.log.extend(audits)
        self.summary = summarize(audits)
        self.month += 1
        return events


class CombinedLedger:
    def __init__(self, books):
        self.books = books

    def after_receipts(self, wallet, start, end):
        for book in self.books:
            yield from book.after_receipts(wallet, start, end)

    @property
    def summary(self):
        return {key: value for book in self.books for key, value in book.summary.items()}


def make(scenario, tax_ledger=None):
    from wealthlab.portfolio.saving_household import Ledger as SavingLedger
    from wealthlab.products.drilling_household import Ledger as DrillingLedger
    from wealthlab.products.exchange_fund_household import Ledger as ExchangeLedger
    from wealthlab.products.life_household import Ledger as LifeLedger

    books: list = [Ledger(scenario)] if scenario.sleeve_plan else []
    if scenario.exchange_fund_plan:
        books.append(ExchangeLedger(scenario))
    if scenario.life_plan:
        books.append(LifeLedger(scenario, tax_ledger))
    if scenario.drilling_plan:
        books.append(DrillingLedger(scenario))
    if scenario.lot_plan and scenario.lot_plan.savings:
        books.append(SavingLedger(scenario, tax_ledger))
    return CombinedLedger(books) if books else None


def completed(ledger):
    return ledger.summary if ledger else {}


def finish(ledger, rows):
    if ledger:
        for book in ledger.books:
            finish_book(book, rows)


def finish_book(book, rows):
    if hasattr(book, "finish"):
        book.finish(rows)
        return
    record_exits(book, rows)
    rows[-1]["sleeve_tax_assumptions"] = [
        tax_audit(a) for s in book.plan.sleeves for a in s.allocations
    ]
