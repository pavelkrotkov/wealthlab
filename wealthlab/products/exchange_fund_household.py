"""A single exchange book shares actual household cash, annual taxes and consumption funding."""

from wealthlab.products import exchange_fund_lots as lots
from wealthlab.products.conditional_allocations import events as allocation_events
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
        self.is_exchange = self.plan.mode == "exchange" and self.plan.accepted
        self.pending = scheduled_allocations(self.plan)
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
        self.pending.extend(advance(self, observation, wallet))
        events = [e for e in self.pending if start <= e.date < end]
        self.pending = [e for e in self.pending if e.date >= end]
        self.summary = summarize(self.log[-1], self.plan)
        return events

    def finish(self, rows):
        """Keep immutable terms, one contribution event and every actual ending share."""
        rows[-1]["exchange_fund_audit"] = dict(
            terms=self.plan.model_dump(mode="json"),
            months=self.log,
            remaining_lots=[lot.model_dump(mode="json") for lot in self.book.lots.values()],
            disposals=self.book.disposals,
            opening_contribution_events=[e.model_dump(mode="json") for e in self.opening_events],
            unrecognized_future_events=[e.model_dump(mode="json") for e in self.pending],
            terminal_state=dict(
                active=self.active,
                nav=self.nav,
                cash=sum(self.book.cash.values(), lots.ZERO),
                fees_due=sum(self.book.fee_owed.values(), lots.ZERO),
                opening_cash_due=self.initial_cash,
                interest_basis=dict(self.bases),
            ),
            conditional=True,
        )


def scheduled_allocations(plan):
    """Final K-1 and deferred losses follow recognition dates, even after economic exit."""
    if plan.mode != "exchange" or not plan.accepted:
        return []
    return [e for o in plan.observations for e in allocation_events(o.allocation)]


def summarize(row, plan):
    """Report restricted NAV separately from actually received cash and liquid shares."""
    summary = {
        "exchange_" + key: value
        for key, value in row.items()
        if key not in {"date", "account_value"}
    }
    summary["exchange_liquid_value"] = row["account_value"] - row["locked_value"]
    summary["exchange_acceptance_denied"] = plan.mode == "exchange" and not plan.accepted
    return summary
