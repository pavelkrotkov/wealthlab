"""Retain only requested actually observed valuation cutoffs, never supplied future forecasts."""

from wealthlab.household.advisory_snapshot_values import observed


class Snapshots:
    def __init__(self, plan):
        self.requested = {}
        self.values = {}
        for schedule in plan.schedules:
            for period in schedule.periods:
                key = period.valuation_date, period.valuation_cutoff
                self.requested.setdefault(key, set()).update(c.account_id for c in schedule.covered)

    def capture(self, cutoff, when, wallet, life, debts):
        key = when, cutoff
        if key not in self.requested:
            return
        if key in self.values:
            raise ValueError("An advisory valuation snapshot cannot be observed twice.")
        self.values[key] = observed(self.requested[key], when, cutoff, wallet, life, debts)

    def resolve(self, period):
        key = period.valuation_date, period.valuation_cutoff
        if key not in self.values:
            raise ValueError("Advisory valuation snapshot is unavailable at this billing cutoff.")
        return self.values[key]

    def export(self):
        return [self.values[key] for key in sorted(self.values)]
