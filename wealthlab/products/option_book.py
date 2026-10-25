"""Finite reserves, explicit settlement debt, and segregated configurable collateral."""

from decimal import Decimal

from wealthlab.portfolio.book import Book


class OptionBook:
    def __init__(self, case):
        self.case = case
        self.book = Book(case.holdings)
        self.account = case.holdings.accounts[0].id
        self.reserve = case.outside_cash
        self.loan = Decimal(0)
        self.collateral = Decimal(0)
        self.active = {}
        self.closed = {}
        self.rows = []
        self.recognition = []
        self.failures = []
        self.entitlements = {}
        self.cash_movements = []

    def fund(self, amount, *, require_full=False):
        deficit = max(Decimal(0), amount - self.book.cash[self.account])
        if require_full and not self.case.allow_settlement_loan and deficit > self.reserve:
            return False
        transfer = min(deficit, self.reserve)
        self.reserve -= transfer
        self.book.cash[self.account] += transfer
        deficit -= transfer
        if deficit and self.case.allow_settlement_loan:
            self.loan += deficit
            self.book.cash[self.account] += deficit
            deficit = Decimal(0)
        return not deficit

    def cash(self, amount, label, day):
        if amount < 0:
            self.fund(-amount)
        # Cash-settlement liabilities survive an exhausted reserve; no limited liability inferred.
        self.book.cash[self.account] += amount
        self.cash_movements.append(dict(date=day.isoformat(), label=label, amount=amount))
