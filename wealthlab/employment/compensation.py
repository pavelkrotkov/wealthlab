"""One employer-value book; only the existing tax ledger deposits funded cash.

Vesting changes the vested/contingent split without depositing money. A payout
removes its source value first, then sends one actual receipt to the tax ledger.
This order preserves capital even when a requested distribution cannot be paid.
"""

from decimal import Decimal

from wealthlab.employment.compensation_events import Allocation, Distribution
from wealthlab.employment.compensation_operations import OPERATIONS
from wealthlab.employment.compensation_validation import validate
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


class Ledger:
    def __init__(self, scenario):
        validate(scenario)
        self.plan = scenario.compensation_plan
        self.accounts = {a.id: a for a in scenario.accounts}
        self.tranches = {t.id: t for t in self.plan.tranches}
        self.states = {
            t.id: dict(vested=t.opening_vested, unvested=t.opening_unvested)
            for t in self.plan.tranches
        }
        self.events = sorted(self.plan.events, key=lambda e: (e.date, e.sequence))
        self.log = []

    def month(self, wallet, start, end):
        taxes = []
        self.requested = self.distributed = Decimal(0)
        for event in self.events:
            if not start <= event.date < end:
                continue
            tranche = self.tranches[event.tranche]
            if isinstance(event, Allocation):
                continue
            state = self.states[event.tranche]
            before = dict(state)
            paid = OPERATIONS[event.kind](state, event, tranche)
            wallet.balances[tranche.account] += state["vested"] - before["vested"]
            if isinstance(event, Distribution):
                self.requested += event.amount if event.election == "cash" else Decimal(0)
                self.distributed += paid
            self.log.append(
                dict(
                    event=event.id,
                    date=event.date,
                    tranche=tranche.id,
                    kind=event.kind,
                    before=before,
                    after=dict(state),
                    cash=paid,
                    requested_amount=getattr(event, "amount", None),
                )
            )
            if paid:
                taxes.append(
                    TaxEvent(
                        date=event.date,
                        description=event.id,
                        cash_received=paid,
                        federal=FederalIncome(),
                        new_jersey=NJIncome(),
                    )
                )
        return taxes
