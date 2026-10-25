"""Persistent actual option book runs after receipts and before competing optional deposits."""

from wealthlab.products.option_book import OptionBook
from wealthlab.products.option_engine import complete_unwind
from wealthlab.products.option_events import open_leg
from wealthlab.products.option_financing import accrue
from wealthlab.products.option_household_cash import settle
from wealthlab.products.option_household_reporting import completed, finish  # noqa: F401
from wealthlab.products.option_household_tax import events
from wealthlab.products.option_household_validation import validate
from wealthlab.products.option_reporting import snapshot
from wealthlab.products.option_tax import yearend
from wealthlab.products.option_timing import dividends, terminations


class Ledger:
    def __init__(self, scenario, market):
        validate(scenario, market)
        self.plan = scenario.option_plan
        self.state = OptionBook(self.plan.case)
        self.seen = set()
        self.previous = scenario.start
        self.log = []
        self.summary = {}

    def after_receipts(self, wallet, start, end):
        state = self.state
        before = wallet.cash
        state.reserve = before
        marks = [mark for mark in self.plan.case.marks if start <= mark.date < end]
        for mark in marks:
            self.advance(mark)
        if marks[-1].date == self.plan.case.holdings.end and self.plan.case.unwind:
            complete_unwind(state, marks[-1])
        settle(self, wallet, before, marks[-1])
        return events(state, start, end, self.seen)

    def advance(self, mark):
        accrue(self.state, self.previous, mark.date)
        self.previous = mark.date
        dividends(self.state, mark)
        terminations(self.state, mark, same_day=False)
        for leg in self.plan.case.legs:
            if leg.opened == mark.date:
                open_leg(self.state, leg, mark)
        terminations(self.state, mark, same_day=True)
        yearend(self.state, mark)
        row = snapshot(self.state, mark)
        row["execution_failed"] = bool(self.state.failures)


def make(scenario, market=None):
    return Ledger(scenario, market) if scenario.option_plan else None
