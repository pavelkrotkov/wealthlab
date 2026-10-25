"""Manual linked trades share actual household cash and month-end market marks.

A buy can use brokerage cash or already received household cash, never future
salary or automatic borrowing. A sweep transfers remaining brokerage cash once;
linked account values then contain only actual marked shares. Manual orders
retain their dated/list order within the household's monthly cash convention.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio import household_policies, household_wash, rebalance
from wealthlab.portfolio import household_recognition as recognition
from wealthlab.portfolio.book import Book
from wealthlab.portfolio.household_validation import validate
from wealthlab.portfolio.household_values import account_value

ZERO = Decimal(0)


class Ledger:
    def __init__(self, scenario):
        validate(scenario)
        self.scenario = scenario
        self.plan = scenario.lot_plan
        self.case = self.plan.case
        self.book = Book(self.case)
        self.marks = {m.date: m.prices for m in self.plan.monthly_marks}
        self.reported = {}
        self.prices = self.plan.opening_prices
        self.when = self.case.as_of
        self.counter = 0
        self.monthly = {}
        self.locked = set()
        self.funding_orders = []
        self.sale_decisions = []
        self.rebalance_decisions = []
        self.book.allocated_ids.update(p.id for p in self.plan.rebalances)
        self.reconciliations = []

    def after_receipts(self, wallet, start, end):
        self.when = end - timedelta(days=1)
        self.prices = self.marks[self.when]
        supplied = ZERO
        for trade in self.case.trades:
            if start <= trade.date < end:
                supplied += manual(self.book, wallet, trade)
        household_policies.execute(self, wallet, start, end)
        rebalance.execute(self, start, end)
        swept = sweep(self.book, wallet)
        sync(self.book, wallet, self.prices)
        self.monthly = dict(
            lot_purchase_cash_supplied=supplied, lot_cash_swept=swept, lot_funding_proceeds=ZERO
        )
        household_wash.observe(self)
        return (
            recognition.event(
                self.case,
                self.book,
                self.when,
                self.reported,
                allow_pending=self.plan.year_end_wash_policy == "january_reconcile",
            ),
        )

    def pending(self, year):
        return household_wash.pending(self, year)

    def finish(self, rows):
        household_wash.finish(self, rows)
        rows[-1]["lot_audit"] = dict(
            account_values={a: rows[-1]["account_balances"][a] for a in self.book.accounts},
            lots=[lot.model_dump(mode="json") for lot in self.book.lots.values()],
            disposals=self.book.disposals,
            trades=[t.model_dump(mode="json") for t in self.book.history],
            funding_orders=self.funding_orders,
            sale_decisions=self.sale_decisions,
            rebalance_decisions=self.rebalance_decisions,
            harvest_decisions=self.book.harvest_decisions,
            closing_prices=dict(self.prices),
            recognized_by_year=dict(self.reported),
            nj_wash_treatment=self.case.nj_wash_treatment,
            return_reconciliations=self.reconciliations,
        )


def manual(book, wallet, trade):
    supplied = ZERO
    if trade.action == "buy":
        required = money(trade.quantity * trade.price) + trade.commission
        supplied = max(ZERO, required - book.cash[trade.account_id])
        if wallet.pay(supplied) != supplied:
            raise ValueError("Manual linked share purchases cannot borrow or use future receipts.")
        book.cash[trade.account_id] += supplied
    book.trade(trade)
    return supplied


def sweep(book, wallet):
    total = sum(book.cash.values(), ZERO)
    wallet.deposit(total)
    book.cash = dict.fromkeys(book.cash, ZERO)
    return total


def sync(book, wallet, prices):
    for identity in book.accounts:
        wallet.balances[identity] = account_value(
            book.lots.values(), identity, book.cash[identity], prices
        )


def make(scenario):
    return Ledger(scenario) if scenario.lot_plan else None


def completed(ledger):
    return ledger.monthly if ledger is not None else {}


def finish(ledger, rows):
    if ledger is not None:
        ledger.finish(rows)
