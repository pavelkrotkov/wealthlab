"""Optional investments reuse the live lot book, wash history and annual recognition.

These purchases follow product cash and precede optional wrapper deposits. They
reserve current modeled bills and tax plus an explicit cash buffer. Unfilled
saving is reported separately from mandatory household funding failures.
"""

from decimal import Decimal

from wealthlab.portfolio import household_recognition, household_wash
from wealthlab.portfolio.saving_cash import execute
from wealthlab.portfolio.saving_validation import validate


class Ledger:
    def __init__(self, scenario, tax):
        self.plan, self.tax, self.lots = scenario.lot_plan, tax, tax.lots
        validate(self.plan, scenario)
        self.lots.book.allocated_ids.update(p.id for p in self.plan.savings)
        self.log, self.summary = [], {}

    def after_receipts(self, wallet, start, end):
        rows = []
        for policy in sorted(self.plan.savings, key=lambda p: p.date):
            if start <= policy.date < end:
                row = execute(self.lots, self.tax, policy, wallet, start, end)
                rows.append(row)
                self.log.append(row)
                household_wash.observe(self.lots)
                yield household_recognition.event(
                    self.lots.case,
                    self.lots.book,
                    self.lots.when,
                    self.lots.reported,
                    allow_pending=self.plan.year_end_wash_policy == "january_reconcile",
                )
        self.summary = {
            f"saving_{name}": sum((r[name] for r in rows), Decimal(0))
            for name in ("requested", "spent", "unfilled", "commissions")
        }

    def finish(self, rows):
        rows[-1]["saving_audit"] = self.log
