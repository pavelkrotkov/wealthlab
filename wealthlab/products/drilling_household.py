"""One wallet supplies calls and receives distributions; tax recognition has zero cash."""

from wealthlab.products import drilling_cash as cash
from wealthlab.products.drilling_reference import advance as reference_step
from wealthlab.products.drilling_reference import opening as reference_opening
from wealthlab.products.drilling_reporting import finish, summary
from wealthlab.products.drilling_step import step
from wealthlab.products.drilling_validation import validate


class Ledger:
    def __init__(self, scenario):
        validate(scenario)
        self.plan = scenario.drilling_plan
        self.cash = self.plan.opening_cash
        self.property_value = self.plan.opening_property_value
        self.bases = dict(
            federal=self.plan.opening_federal_basis,
            nj=self.plan.opening_nj_basis,
            at_risk=self.plan.opening_at_risk,
        )
        self.tangible_basis = dict(
            federal=self.plan.opening_federal_tangible_basis, nj=self.plan.opening_nj_tangible_basis
        )
        self.owed = dict.fromkeys((*cash.COSTS, "exit_cost"), cash.ZERO)
        self.call_owed = cash.ZERO
        self.property_sold = self.closed = False
        self.pending, self.log, self.summary = [], [], {}
        self.reference_case, self.reference_book = reference_opening(self.plan, scenario)
        self.reference_exit_pending = False
        self.reference_reported = {}

    def after_receipts(self, wallet, start, end):
        observation = next(o for o in self.plan.observations if start <= o.date < end)
        if self.plan.mode == "liquid_reference":
            row, events = reference_step(self, observation, wallet)
        else:
            row, events = step(self, observation, wallet)
        self.pending.extend(events)
        current = take_events(self, start, end)
        self.log.append(row)
        self.summary = summary(row)
        return current

    def finish(self, rows):
        finish(self, rows)


def take_events(ledger, start, end):
    current = [e for e in ledger.pending if start <= e.date < end]
    ledger.pending = [e for e in ledger.pending if e.date >= end]
    return current
