"""One required-tax book owns foreign cash while the existing ledger owns US tax.

The immutable plan supplies assessments, actual opening records and source
classifications. Execution changes the shared wallet once, retains original
native balances and refreshes only this book's federal credit facts.

Actual bank cash, foreign levy translation and the country-recognized applied
amount remain distinct. The latter changes only its assessment position; it
does not withdraw a second payment or select US creditability.
"""

from datetime import timedelta
from decimal import Decimal
from functools import partial

from wealthlab.tax.foreign_tax_credits import carry_reasons, opening_carries, refresh
from wealthlab.tax.foreign_tax_execution import pay_due
from wealthlab.tax.foreign_tax_positions import position_reasons, snapshot
from wealthlab.tax.foreign_tax_recognition import supplied
from wealthlab.tax.foreign_tax_refunds import receive_refunds
from wealthlab.tax.foreign_tax_reporting import report
from wealthlab.tax.foreign_tax_sources import history, payment_record
from wealthlab.tax.foreign_tax_validation import cash_records, validate
from wealthlab.tax.pr_execution_credit_sources import household_annual

ZERO = Decimal(0)


class ForeignTaxBook:
    def __init__(self, scenario):
        self.plan = scenario.foreign_tax_plan
        validate(self.plan, scenario)
        self.assessments = {a.id: a for a in self.plan.assessments}
        self.quotes = {(q.date, q.currency): q for q in self.plan.quotes}
        self.profiles = {p.annual.policy.year: p for p in self.plan.credit_profiles}
        self.payments = [(p.assessment_id, payment_record(p)) for p in self.plan.opening_payments]
        self.filled = {p.id: ZERO for p in self.plan.schedules}
        self.executions, self.schedule_by_payment = {}, {}
        self.recognized_native = supplied(self.plan)
        self.reserved_ids = {p.record.id for p in cash_records(self.plan)}
        self.credit_results = {}
        self.month_records, self.log = [], []
        self.month = None
        self.sales_observed = ZERO
        self.retrying = False

    def observed_ids(self):
        return {r.id for _, r in self.payments}

    def income_history(self, when=None):
        return history(self.profiles.values(), when)[0]

    def credit_case(self, year, when, annual=None, extra=()):
        profile = self.profiles[year]
        return profile.model_copy(
            update=dict(
                annual=household_annual(annual or profile.annual),
                as_of=when,
                income=self.income_history(when),
                opening_carries=opening_carries(self, year),
                tax_cash=[r for _, r in self.payments if r.value.date <= when] + list(extra),
            )
        )

    def before_optional(self, ledger, wallet, start, end):
        self.month, self.month_records = (start, end), []
        receive_refunds(self, wallet, start, end)
        self.retry(ledger, wallet, start, end)

    def retry(self, ledger, wallet, start, end):
        if self.retrying:
            return
        self.retrying = True
        try:
            when = end - timedelta(days=1)
            refresh(self, ledger, when)
            pay_due(self, ledger, wallet, start, end, when)
            refresh(self, ledger, when)
        finally:
            self.retrying = False

    def finish_month(self, ledger, start, end):
        when = end - timedelta(days=1)
        result = refresh(self, ledger, when)
        self.sales_observed += ledger.funding_context["proceeds"]
        unresolved = list(result["unresolved"]) + carry_reasons(self, when.year)
        if self.sales_observed:
            unresolved.append(
                "Actual funding sales require independent foreign gain/source/basis classification."
            )
        if any(
            r.record.value.date <= when and r.record.id not in self.observed_ids()
            for r in self.plan.source_withholding
        ):
            unresolved.append("Planned foreign source withholding lacks its actual linked receipt.")
        positions = snapshot(self, when)
        unresolved.extend(position_reasons(self, positions))
        if any(a.eligibility != "allowed" for a in self.plan.assessments if a.observed <= when):
            unresolved.append("One or more supplied foreign assessments remain denied/unresolved.")
        row = report(self, when, positions, unresolved)
        self.log.append(row)
        return row


def make(scenario):
    return ForeignTaxBook(scenario) if scenario.foreign_tax_plan else None


def before_optional(ledger, wallet, start, end):
    if ledger.foreign is not None:
        ledger.foreign.before_optional(ledger, wallet, start, end)


def completed(ledger, start, end):
    return ledger.foreign.finish_month(ledger, start, end) if ledger.foreign else {}


def refresh_credit(ledger, end):
    if ledger.foreign is not None:
        refresh(ledger.foreign, ledger, end - timedelta(days=1))


def reconcile_required(ledger, wallet, start, end):
    if ledger.foreign is None:
        return
    refresh_credit(ledger, end)
    if ledger.funding_context["proceeds"]:
        # A real sale can invalidate an earlier foreign credit. Fund the now
        # known domestic bill without retaining that stale favorable claim.
        ledger.fund_required(wallet, ZERO, start, end)
        refresh_credit(ledger, end)


def receipt_priority(ledger):
    if ledger is None or ledger.foreign is None:
        return None
    return partial(retry, ledger)


def retry(ledger, wallet, start, end):
    ledger.foreign.retry(ledger, wallet, start, end)
