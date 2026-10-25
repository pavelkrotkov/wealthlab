"""Outer fee assessment is noncash; actual payments and arrears reuse the household fee bill."""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.advisory_assessment import assess
from wealthlab.household.advisory_snapshots import Snapshots
from wealthlab.household.advisory_validation import validate

ZERO = Decimal(0)


class Ledger:
    def __init__(self, scenario, observations):
        validate(scenario)
        self.scenario, self.plan, self.observations = (
            scenario,
            scenario.advisory_fee_plan,
            observations,
        )
        self.assessments, self.payments = [], []
        self.owed, self.current_due, self.reserve_amount = ZERO, ZERO, ZERO
        self.previous_fees_owed, self.fixed_due = ZERO, ZERO
        self.monthly = []
        self.seen = set()
        self.summary = {}
        self.snapshots = Snapshots(self.plan)

    def begin(self, previous, fixed):
        self.previous_fees_owed, self.fixed_due = previous, fixed
        self.current_due, self.monthly = ZERO, []
        self.reserve_amount = previous + fixed

    def after_receipts(self, wallet, start, end):
        when = end - timedelta(days=1)
        if when in self.seen:
            raise ValueError("An advisory snapshot cannot be assessed twice.")
        self.seen.add(when)
        # Every simultaneous schedule uses the same pre-payment/pre-saving snapshot.
        self.snapshots.capture(
            "product_marks_before_optional_saving",
            when,
            wallet,
            self.observations().get("life_policy_values", []),
            {},
        )
        self.monthly = [
            self.assessment(schedule, period)
            for schedule in self.plan.schedules
            for period in schedule.periods
            if period.assessment_date == when
        ]
        self.assessments.extend(self.monthly)
        self.current_due = sum((a["assessed"] for a in self.monthly), ZERO)
        self.owed += self.current_due
        self.reserve_amount += self.current_due
        return ()

    def assessment(self, schedule, period):
        snapshot = self.snapshots.resolve(period)
        return assess(schedule, period, snapshot["account_net_equity"], snapshot["life_values"])

    def settle(self, fee_row, when):
        prior_advisory = self.owed - self.current_due
        prior_generic = self.previous_fees_owed - prior_advisory
        # Existing arrears precede new bills. Within each age bucket, generic fees
        # precede advisory fees; this only attributes the existing combined payment.
        old_paid = min(prior_advisory, max(ZERO, fee_row["fees"] - prior_generic))
        remaining = max(ZERO, fee_row["fees"] - self.previous_fees_owed - self.fixed_due)
        paid = old_paid + min(self.current_due, remaining)
        self.owed -= paid
        self.payments.append(dict(date=when.isoformat(), paid=paid, remaining_owed=self.owed))
        self.summary = dict(
            advisory_fees_assessed=self.current_due,
            advisory_fees_paid=paid,
            advisory_fees_owed=self.owed,
            advisory_fee_assessments=self.monthly,
        )
        return self.summary

    def finish(self, rows):
        rows[-1]["advisory_fee_audit"] = dict(
            inputs=self.plan.model_dump(mode="json"),
            assessments=self.assessments,
            payments=self.payments,
            remaining_owed=self.owed,
            payment_attribution="generic prior, advisory prior, generic current, advisory current",
            automatic_tax_deduction=False,
            observed_snapshots=self.snapshots.export(),
        )
