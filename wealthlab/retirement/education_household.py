"""Actual 529 funding, direct tuition payments and household cash fallback.

Tuition requests are net, qualified institution bills outside ordinary budgets.
Only the paid wrapper portion leaves 529 assets; ordinary cash pays the rest
later in the spending order. A remaining bill is a visible spending shortfall.
"""

from decimal import Decimal

from wealthlab.retirement import education
from wealthlab.retirement.education_household_case import annual_case
from wealthlab.retirement.education_household_validation import validate
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent

ZERO = Decimal(0)


class Ledger:
    def __init__(self, scenario):
        validate(scenario)
        self.scenario = scenario
        self.year = scenario.start.year
        self.book = education.opening(annual_case(scenario, self.year))
        self.events = education.timeline(self.book["case"])
        self.orders, self.years = [], []
        self.cash_need = ZERO
        self.direct_paid = ZERO
        self.summary = {}

    def begin(self, year, wallet):
        if year != self.year:
            case = annual_case(self.scenario, year, wallet.balances, self.book["basis"])
            self.book = education.opening(case)
            self.events = education.timeline(case)
            self.year = year

    def after_receipts(self, wallet, start, end):
        self.begin(start.year, wallet)
        self.book["cash"] = wallet.cash
        offset = len(self.book["rows"])
        before = self.book["nj_contributions"]
        for when, _, _, item in self.events:
            if start <= when < end:
                education.apply(self.book, item)
        difference = self.book["cash"] - wallet.cash
        wallet.pay(-difference)
        wallet.balances.update(self.book["balances"])
        rows = self.book["rows"][offset:]
        self.orders.extend(rows)
        withdrawals = [r for r in rows if r["kind"] == "withdrawal"]
        self.direct_paid = sum((r["funded"] for r in withdrawals), ZERO)
        self.cash_need = sum((r["unfilled"] for r in withdrawals), ZERO)
        self.summary = deposit_summary(rows)
        return (
            TaxEvent(
                date=start,
                description="Funded NJBEST deposits; qualification uses final NJ income",
                cash_received=0,
                federal=FederalIncome(),
                new_jersey=NJIncome(),
                njbest_contributions=self.book["nj_contributions"] - before,
            ),
        )

    def fund(self, wallet):
        cash_paid = wallet.pay(self.cash_need)
        return dict(
            education_wrapper_paid=self.direct_paid,
            education_cash_fallback=cash_paid,
            education_tuition_unfunded=self.cash_need - cash_paid,
            **self.summary,
        )

    def completed(self, end, tax_result):
        if end.year > self.year:
            case = self.book["case"].model_copy(
                update=dict(nj_gross_income=tax_result["new_jersey"]["gross_income"])
            )
            self.years.append(
                dict(
                    year=self.year,
                    rule_mode=self.book["case"].rule_mode,
                    contribution_basis=dict(self.book["basis"]),
                    closed_account_loss_basis=self.book["loss_basis"],
                    investment_return=self.book["return"],
                    **education.reconcile(case, self.book),
                )
            )

    def finish(self, rows):
        rows[-1]["education_audit"] = dict(orders=self.orders, years=self.years)


def deposit_summary(rows):
    deposits = [r for r in rows if r["kind"] == "contribution"]
    return dict(
        education_deposits=sum((r["funded"] for r in deposits), ZERO),
        education_unfilled_deposits=sum(
            (r["unfunded"] + r["blocked_by_limit"] for r in deposits), ZERO
        ),
    )


def make(scenario):
    return Ledger(scenario) if scenario.education_plan else None


def fund(ledger, wallet):
    return ledger.fund(wallet) if ledger is not None else {}


def completed(ledger, tax_ledger, end):
    if ledger is not None:
        ledger.completed(end, tax_ledger.result)


def finish(ledger, rows):
    if ledger is not None:
        ledger.finish(rows)
