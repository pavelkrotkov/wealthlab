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


class Ledger:
    def __init__(self, scenario):
        validate(scenario)
        self.plan = scenario.sleeve_plan
        self.books = {s.account_id: opening(s.case) for s in self.plan.sleeves}
        self.allocations = {
            s.account_id: [e for a in s.allocations for e in tax_events(a)]
            for s in self.plan.sleeves
        }
        self.month = 0
        self.log = []
        self.summary = {}

    def after_receipts(self, wallet, start, end):
        audits, events = [], []
        for sleeve in self.plan.sleeves:
            audits.append(execute(self.books[sleeve.account_id], sleeve, self.month, wallet, end))
            events.extend(a for a in self.allocations[sleeve.account_id] if start <= a.date < end)
        self.log.extend(audits)
        self.summary = summarize(audits)
        self.month += 1
        return events


def make(scenario):
    return Ledger(scenario) if scenario.sleeve_plan else None


def completed(ledger):
    return ledger.summary if ledger else {}


def finish(ledger, rows):
    if ledger:
        rows[-1]["sleeve_audit"] = ledger.log
        rows[-1]["sleeve_tax_assumptions"] = [
            tax_audit(a) for s in ledger.plan.sleeves for a in s.allocations
        ]
