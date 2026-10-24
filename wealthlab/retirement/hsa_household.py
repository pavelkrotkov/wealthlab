"""Reuse the HSA cash and receipt book without inventing household tax savings.

Historical paid receipts and current unpaid bills have distinct books. Only
actual medical payments create new receipt capacity; unpaid bills remain
liabilities. Nonqualified distributions and provider payments use actual
funded amounts and explicit federal/NJ assumptions.
Cash-only accounts retain their explicit conditional NJ bank assumption.
Invested accounts persist one lot book across annual eligibility resets. Their
wallet value includes marked securities and receivables; withdrawal capacity
uses actual cash after eligible sales, commissions and prior custodian fees.
Investment NJ income enters a separate zero-cash event. Fee arrears remain a
separate household liability, preserving actual gross account values.
"""

from datetime import date

from wealthlab.retirement import hsa
from wealthlab.retirement.hsa_household_events import apply as apply_events
from wealthlab.retirement.hsa_household_reporting import annual, summary
from wealthlab.retirement.hsa_household_tax import annotate, totals
from wealthlab.retirement.hsa_household_tax import event as tax_event
from wealthlab.retirement.hsa_household_validation import annual_case, validate
from wealthlab.retirement.hsa_invested_household import Investments
from wealthlab.retirement.medical_bills import Bills


class Ledger:
    def __init__(self, scenario):
        validate(scenario)
        self.plan = scenario.hsa_plan
        self.accounts = [a for a in scenario.accounts if a.wrapper == "hsa"]
        self.year = scenario.start.year
        context = next(y for y in self.plan.years if y.year == self.year)
        self.context = context
        case = annual_case(self.plan, context, self.accounts)
        self.book = hsa.opening(case)
        self.investments = Investments(self.plan.investments) if self.plan.investments else None
        if self.investments is not None:
            self.investments.attach(self.book)
        self.medical = Bills(self.plan.medical_bills)
        self.medical.initialize_receipts(self.book)
        self.events = timeline(self.plan, case)
        self.audit = []
        self.annual = []
        self.summary = {}

    def begin(self, year, wallet):
        if self.year == year:
            return
        remaining = self.book["receipt_remaining"]
        context = next(y for y in self.plan.years if y.year == year)
        accounts = [a.model_copy(update=dict(balance=wallet.balances[a.id])) for a in self.accounts]
        self.context = context
        case = annual_case(self.plan, context, accounts)
        self.book = hsa.opening(case)
        self.book["receipt_remaining"] = remaining
        if self.investments is not None:
            self.investments.attach(self.book)
        self.events = timeline(self.plan, case)
        self.year = year

    def after_receipts(self, wallet, start, end):
        self.begin(start.year, wallet)
        self.medical.start(start, end)
        self.book["cash"] = wallet.cash
        before = {key: self.book[key] for key in ("personal", "employer", "interest")}
        offset = len(self.book["rows"])
        apply_events(self, start, end)
        rows = self.book["rows"][offset:]
        validate_employer_funding(rows)
        annotate(rows, self.plan)
        difference = self.book["cash"] - wallet.cash
        if difference >= 0:
            wallet.deposit(difference)
        else:
            wallet.pay(-difference)
        wallet.balances.update(self.book["balances"])
        if self.investments is not None:
            self.investments.wallet(wallet)
        self.audit.extend(rows)
        amounts = {key: self.book[key] - before[key] for key in before}
        amounts.update(totals(rows))
        self.summary = summary(rows, amounts)
        if self.investments is not None:
            self.summary.update(self.investments.summary())
            return tax_event(start, amounts), self.investments.event(start)
        return (tax_event(start, amounts),)

    def completed(self, end):
        if end == date(self.year + 1, 1, 1):
            self.annual.append(annual(self))
        return self.summary

    def finish(self, rows):
        rows[-1]["hsa_audit"] = dict(
            orders=self.audit,
            years=self.annual,
            receipt_remaining=dict(self.book["receipt_remaining"]),
            medical_bills=self.medical.audit(),
            nj_treatment=self.plan.nj_treatment,
            distribution_tax_assumptions=dict(
                federal=self.plan.nonqualified_treatment,
                nj_fractions=self.plan.nj_withdrawal_taxable_fractions,
                duplicate_tax_exclusion_confirmed=(
                    self.plan.generated_distribution_tax_excluded_from_other_inputs_confirmed
                ),
            ),
        )

        if self.investments is not None:
            self.investments.finish(rows[-1]["hsa_audit"])


def make(scenario):
    return Ledger(scenario) if scenario.hsa_plan else None


def completed(ledger, end):
    return ledger.completed(end) if ledger is not None else {}


def finish(ledger, rows):
    if ledger is not None:
        ledger.finish(rows)


def validate_employer_funding(rows):
    if any(r["kind"] == "direct_employer" and r["blocked_by_limit"] for r in rows):
        raise ValueError("Excess employer HSA funding needs the payroll/correction adapter.")


def timeline(plan, case):
    bills = [
        (b.date, 4, i, b) for i, b in enumerate(plan.medical_bills) if b.date.year == case.year
    ]
    return sorted([*hsa.timeline(case), *bills], key=lambda event: event[:3])


def fund_medical(ledger, wallet):
    return ledger.medical.fund(wallet, ledger.book) if ledger is not None else {}
