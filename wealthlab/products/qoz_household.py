"""Actual gain-backed calls and entity cash use the existing household wallet and tax ledger."""

from datetime import timedelta

from wealthlab.products import qoz_economics as economics
from wealthlab.products.long_short_book import ZERO
from wealthlab.products.qoz_calls import fund
from wealthlab.products.qoz_execution import execute
from wealthlab.products.qoz_validation import validate


class Ledger:
    """One run keeps economic books separate from original-source tax recognition.

    Each funded call owns its own clock and mixed qualifying/nonqualifying basis.
    Month-end source sales have already swept actual cash into the shared wallet.
    No predicted tax saving supplies a call; the annual ledger later funds taxes.
    Internal loans are entity obligations, while only stock NAV and settlement
    receivables enter the shareholder account. Every settlement deposits once.
    """

    def __init__(self, scenario, lots, tax):
        validate(scenario, lots, tax)
        self.plan, self.lots, self.tax_ledger = scenario.qoz_plan, lots, tax
        self.tranches, self.used, self.log, self.calls = [], {}, [], []
        self.summary = {}

    def after_receipts(self, wallet, start, end):
        when = end - timedelta(days=1)
        observation = next(o for o in self.plan.observations if o.date == when)
        row, events = (
            dict(
                date=when.isoformat(),
                call_paid=ZERO,
                call_unfunded=ZERO,
                dividends=ZERO,
                settlement_cash=ZERO,
                original_gain_included=ZERO,
            ),
            [],
        )
        self.advance(observation)
        events.extend(self.fund_calls(wallet, when, row))
        for tranche in self.tranches:
            events.extend(execute(self, tranche, observation, wallet, row))
        row.update(self.values())
        wallet.balances[self.plan.account_id] = row["nav"]
        self.summary = {"qoz_" + key: value for key, value in row.items() if key != "date"}
        self.log.append(row)
        return events

    def advance(self, observation):
        for tranche in self.tranches:
            if not tranche["sold"]:
                tranche["economic_log"].append(economics.step(tranche, observation))

    def fund_calls(self, wallet, when, row):
        events = []
        for call in self.plan.calls:
            if call.date == when:
                created, exclusion, audit = fund(self, call, wallet)
                if created is not None:
                    self.tranches.append(created)
                    events.append(exclusion)
                self.calls.append(audit)
                row["call_paid"] += audit["funded"]
                row["call_unfunded"] += call.amount - audit["funded"]
        return events

    def values(self):
        return dict(
            nav=sum((economics.value(t) for t in self.tranches), ZERO),
            receivable=sum((t["receivable"] for t in self.tranches), ZERO),
            internal_debt=sum((t["book"]["loan"] for t in self.tranches), ZERO),
        )

    def finish(self, rows):
        rows[-1]["qoz_audit"] = dict(
            terms=self.plan.model_dump(mode="json"),
            calls=self.calls,
            months=self.log,
            tranches=[
                {key: value for key, value in t.items() if key != "case"} for t in self.tranches
            ],
        )
