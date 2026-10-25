"""A single exchange book shares actual household cash, annual taxes and consumption funding."""

from wealthlab.products import exchange_fund_lots as lots
from wealthlab.products.exchange_fund_basket import create_basket
from wealthlab.products.exchange_fund_step import advance
from wealthlab.products.exchange_fund_validation import validate


class Ledger:
    def __init__(self, scenario):
        """Separate retained source shares from contributed NAV without duplicating capital.

        Direct sales create taxable gains before reinvesting gross proceeds.
        Actual household cash must therefore pay their taxes or show a shortfall.
        """
        validate(scenario)
        self.plan = scenario.exchange_fund_plan
        self.case, self.book = lots.opening(self.plan, scenario)
        self.prices = self.plan.opening_prices
        self.bases = dict(federal=lots.ZERO, nj=lots.ZERO)
        self.nav = lots.ZERO
        self.active = False
        self.pending = []
        self.initial_cash = lots.ZERO
        self.opening_events = []
        self.log = []
        self.summary = {}
        if self.plan.accepted or self.plan.mode == "direct_sale":
            self.nav, self.bases, event = lots.contribution(self.book, self.plan, scenario.start)
            self.pending.append(event)
            self.opening_events.append(event)
            self.active = self.plan.mode == "exchange"
            if not self.active:
                self.initial_cash = create_basket(
                    self.book,
                    self.plan,
                    self.nav,
                    self.bases,
                    self.prices,
                    scenario.start,
                    direct=True,
                )
                self.nav = lots.ZERO
                self.bases = dict.fromkeys(self.bases, lots.ZERO)

    def after_receipts(self, wallet, start, end):
        wallet.deposit(self.initial_cash)
        self.initial_cash = lots.ZERO
        observation = next(o for o in self.plan.observations if start <= o.date < end)
        events = [*self.pending, *advance(self, observation, wallet)]
        self.pending = []
        row = self.log[-1]
        self.summary = {
            "exchange_" + key: value
            for key, value in row.items()
            if key not in {"date", "account_value"}
        }
        self.summary["exchange_liquid_value"] = row["account_value"] - row["locked_value"]
        self.summary["exchange_acceptance_denied"] = (
            self.plan.mode == "exchange" and not self.plan.accepted
        )
        return events

    def finish(self, rows):
        """Keep immutable terms, one contribution event and every actual ending share."""
        rows[-1]["exchange_fund_audit"] = dict(
            terms=self.plan.model_dump(mode="json"),
            months=self.log,
            remaining_lots=[lot.model_dump(mode="json") for lot in self.book.lots.values()],
            disposals=self.book.disposals,
            opening_contribution_events=[e.model_dump(mode="json") for e in self.opening_events],
            conditional=True,
        )
