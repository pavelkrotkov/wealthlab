"""Premium quotes use completed returns; bills and arrears share ordinary household cash.

The budget is monthly, so payments use that month's pooled resources. Their
first-of-month label is a planning convention, not actual Medicare billing or
Social Security deduction timing. Coverage persists during cash-shortfall tests.
"""

from collections import deque
from datetime import date
from decimal import Decimal

from wealthlab.retirement.medicare import pay, quote
from wealthlab.retirement.medicare_household_validation import validate
from wealthlab.retirement.medicare_inputs import MedicareIncome


class Ledger:
    def __init__(self, scenario):
        validate(scenario)
        self.case = scenario.medicare_plan.case
        self.book: dict = dict(cash=Decimal(0), pending=deque(), rows=[], payments=[])
        self.owed = Decimal(0)
        self.current = []

    def start(self, when):
        self.opening_owed = self.owed
        self.current = [
            quote(self.case, c, when) for c in self.case.coverage if c.start <= when < c.end
        ]
        self.due = sum((r["total_due"] for r in self.current), Decimal(0))
        self.owed += self.due
        self.book["rows"].extend(self.current)
        self.book["pending"].extend(self.current)

    def fund(self, wallet, when):
        before = wallet.cash
        self.book["cash"] = before
        pay(self.book, when)
        paid = wallet.pay(before - self.book["cash"])
        self.owed -= paid
        arrears = min(paid, self.opening_owed)
        newly_unfunded = self.due - max(Decimal(0), paid - self.opening_owed)
        for row in self.current:
            row["unfunded_at_due"] = row["unfunded"]
        return dict(
            medicare_due=self.due,
            medicare_paid=paid,
            medicare_owed=self.owed,
            medicare_arrears_paid=arrears,
            medicare_unfunded=newly_unfunded,
        )

    def observe(self, taxes, end):
        if end != date(taxes.case.policy.year + 1, 1, 1):
            return
        annual = taxes.case
        income = MedicareIncome(
            id=f"household_return_{annual.policy.year}",
            provenance="assumption",
            year=annual.policy.year,
            members=[p.id for p in self.case.members],
            filing="joint" if annual.filing.status == "joint" else "individual",
            agi=taxes.result["federal"]["agi"],
            tax_exempt_interest=annual.federal_income.tax_exempt_interest,
        )
        self.case = self.case.model_copy(
            update=dict(income_history=[*self.case.income_history, income])
        )

    def audit(self):
        return dict(
            bills=self.book["rows"],
            payments=self.book["payments"],
            income_history=[i.model_dump() for i in self.case.income_history],
        )


def make(scenario):
    return Ledger(scenario) if scenario.medicare_plan else None


def start(ledger, when):
    if ledger is not None:
        ledger.start(when)


def observe(ledger, taxes, end):
    if ledger is not None:
        ledger.observe(taxes, end)


def required(ledger):
    return ledger.owed if ledger is not None else Decimal(0)


def fund(ledger, wallet, when):
    return ledger.fund(wallet, when) if ledger is not None else {}


def finish(ledger, rows):
    if ledger is not None:
        rows[-1]["medicare_audit"] = ledger.audit()
