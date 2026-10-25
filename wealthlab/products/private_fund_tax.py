"""Supplied outside basis and actual cash distributions, independent of loss deductibility.

This bounded profile excludes hot assets, debt-share changes and in-kind
payments. Basis adjustments must be independently supplied after applicable
basis rules; denied/deferred tax deductions never silently change basis.
"""

from decimal import Decimal

from wealthlab.markets.wrapper_compile import event_id
from wealthlab.products.conditional_allocations import audit, events
from wealthlab.products.household_inputs import SleeveAllocation


class BasisBook:
    def __init__(self, contract, account_id):
        self.contract = contract
        self.account_id = account_id
        self.basis = dict(
            federal=contract.federal_opening_basis,
            new_jersey=contract.new_jersey_opening_basis,
        )
        self.log = []
        self.deferred = []
        self.closed = False

    def adjust(self, start, end):
        for item in self.contract.basis_adjustments:
            if start <= item.date < end:
                if self.closed:
                    raise ValueError("Basis adjustment after complete liquidation is unsupported.")
                for jurisdiction in self.basis:
                    value = self.basis[jurisdiction] + getattr(item, jurisdiction)
                    if value < 0:
                        raise ValueError("Supplied adjustments cannot make outside basis negative.")
                    self.basis[jurisdiction] = value
                self.log.append(
                    dict(adjustment=item.model_dump(mode="json"), basis=dict(self.basis))
                )

    def distribute(self, amount, final, when):
        values = {}
        opening = dict(self.basis)
        for jurisdiction, basis in self.basis.items():
            values[jurisdiction] = amount - basis if final else max(Decimal(0), amount - basis)
            self.basis[jurisdiction] = Decimal(0) if final else max(Decimal(0), basis - amount)
        item = self.allocation(values, when)
        result = events(item)
        self.closed = final
        self.log.append(
            dict(
                date=when.isoformat(),
                cash=amount,
                complete_liquidation=final,
                opening_basis=opening,
                closing_basis=dict(self.basis),
                conditional_exit=audit(item),
            )
        )
        return result

    def allocation(self, values, when):
        return SleeveAllocation.model_validate(
            dict(
                id=event_id(self.account_id, when, "fund_cash_exit"),
                provenance="assumption",
                date=when,
                federal={self.contract.federal_capital_character: values["federal"]},
                new_jersey=dict(dispositions=values["new_jersey"]),
                federal_loss=self.contract.federal_exit_loss,
                new_jersey_loss=self.contract.new_jersey_exit_loss,
            )
        )

    def release(self, events_due, start, end):
        self.deferred.extend(events_due)
        current = [e for e in self.deferred if start <= e.date < end]
        self.deferred = [e for e in self.deferred if e.date >= end]
        return current
