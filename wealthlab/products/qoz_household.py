"""Actual gain-backed calls and entity cash use the existing household wallet and tax ledger."""

from datetime import timedelta

from wealthlab.products import qoz_economics as economics
from wealthlab.products.long_short_book import ZERO, equity
from wealthlab.products.qoz_calls import fund
from wealthlab.products.qoz_execution import execute
from wealthlab.products.qoz_validation import validate


class Ledger:
    """One run keeps economic books separate from original-source tax recognition.

    Each funded call owns its stock units, clock and mixed qualifying/nonqualifying basis.
    All stock lots share one economic book and creditor position; losses cannot
    vanish between calls. Actual new capital repays debt before buying assets.
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
        self.economic = None
        self.economic_log = []
        self.stock_values = []
        self.revisions = []

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
        events.extend(execute(self, observation, wallet, row))
        row.update(self.values())
        wallet.balances[self.plan.account_id] = row["nav"]
        self.summary = {"qoz_" + key: value for key, value in row.items() if key != "date"}
        self.log.append(row)
        return events

    def advance(self, observation):
        if self.economic is not None and not self.economic["sold"]:
            self.economic_log.append(economics.step(self.economic, observation))

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
        fund = self.economic
        raw = equity(fund["book"]) if fund else ZERO
        return dict(
            entity_equity=raw,
            nonrecourse_deficit=max(ZERO, -raw),
            nav=economics.value(fund) if fund else ZERO,
            receivable=fund["receivable"] if fund else ZERO,
            internal_debt=fund["book"]["loan"] if fund else ZERO,
        )

    def finish(self, rows):
        rows[-1]["qoz_audit"] = dict(
            terms=self.plan.model_dump(mode="json"),
            calls=self.calls,
            source_return_revisions=self.revisions,
            final_source_returns={
                str(year): self.tax_ledger.closed_returns[year].result
                for year in sorted({r["year"] for r in self.revisions})
            },
            months=self.log,
            economic_log=self.economic_log,
            stock_values=self.stock_values,
            ending_entity=self.economic["book"] if self.economic else None,
            tranches=self.tranches,
        )
