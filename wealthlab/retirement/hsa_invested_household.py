"""Translate actual HSA cash movements without turning marked assets into cash.

The persistent lot book survives annual eligibility resets. Only eligible
recipient orders can request liquidation; contributed cash and bank interest
enter the same account exactly once. NJ tax ingredients have zero cash effect.
"""

from decimal import Decimal

from wealthlab.portfolio.fees import settle
from wealthlab.retirement.hsa_investment_reporting import income, receivables, snapshot, values
from wealthlab.retirement.hsa_investments import Ledger
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent

ZERO = Decimal(0)


class Investments:
    def __init__(self, plan):
        self.ledger = Ledger(plan)
        self.accounts = set(self.ledger.book.cash)
        self.recognized = {}

    def attach(self, book):
        book["investments"] = self
        self.sync_balances(book)

    def advance(self, book, when):
        self.ledger.advance(when)
        self.sync_balances(book)

    def sync_balances(self, book):
        book["balances"].update(self.ledger.book.cash)

    def sync_cash(self, book):
        for account in self.accounts:
            self.ledger.book.cash[account] = book["balances"][account]
            settle(self.ledger.book, account)
        self.sync_balances(book)

    def fund(self, book, account, amount, when):
        if account in self.accounts:
            self.advance(book, when)
            self.ledger.raise_cash(account, amount, when)
            self.sync_balances(book)

    def wallet(self, wallet):
        gross, due = values(self.ledger), receivables(self.ledger)
        wallet.balances.update({key: gross[key] + due[key] for key in self.accounts})

    def event(self, when):
        current = income(self.ledger, when.year)
        before = self.recognized.get(when.year, dict.fromkeys(current, ZERO))
        delta = {key: current[key] - before[key] for key in current}
        self.recognized[when.year] = current
        return TaxEvent(
            date=when,
            description="Actual invested-HSA conditional NJ income; federal investment exemption",
            cash_received=0,
            federal=FederalIncome(),
            new_jersey=NJIncome(**delta),
        )

    def summary(self):
        return dict(hsa_investment_fees_owed=sum(self.ledger.book.fee_owed.values(), ZERO))

    def finish(self, audit):
        audit["investments"] = snapshot(self.ledger)
