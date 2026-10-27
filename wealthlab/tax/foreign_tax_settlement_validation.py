"""Cash records retain assessment identity and every marked claim has a dated quote.

Opening payments are already reflected in opening cash. A supplied future
withholding row requires its actual receipt before it becomes paid tax; a
refund retains a distinct original-payment reversal. Revisions cannot amend
an assessment before its original observation, and no missing month-end FX
quote is replaced by a favorable stale annual rate.
"""

from datetime import timedelta

from wealthlab.household.calendar import months
from wealthlab.tax import foreign_tax_recognition


def validate_records(plan, assessments, scenario):
    for item in [*plan.opening_payments, *plan.source_withholding, *plan.refunds]:
        validate_identity(item.record, assessments[item.assessment_id])
        foreign_tax_recognition.validate(item, assessments[item.assessment_id])
    foreign_tax_recognition.validate_opening(plan)
    validate_record_types(plan, scenario)
    validate_scheduled_dates(plan, scenario)
    validate_revisions(plan, assessments)


def validate_identity(record, assessment):
    fields = ("owner_id", "country", "liability_year", "tax_type")
    if any(getattr(record, key) != getattr(assessment, key) for key in fields):
        raise ValueError("Tax cash must retain its assessment's person/jurisdiction/type/year.")


def validate_record_types(plan, scenario):
    if any(r.record.value.date >= scenario.start for r in plan.opening_payments):
        raise ValueError(
            "Opening foreign payments must precede the projection; cash is already paid."
        )
    if any(r.record.kind != "withholding" for r in plan.source_withholding):
        raise ValueError("Linked source withholding needs withholding records.")
    if any(r.record.kind != "refund" for r in plan.refunds):
        raise ValueError("Scheduled foreign refunds need original-payment reversal records.")


def validate_revisions(plan, assessments):
    from wealthlab.tax.foreign_tax_validation import unique

    revisions = [(r.assessment_id, r.observed) for r in plan.revisions]
    unique(revisions, "assessment/date revision")
    if any(r.observed < assessments[r.assessment_id].observed for r in plan.revisions):
        raise ValueError("An assessment revision cannot precede its original observation.")


def validate_quotes(plan, scenario):
    from wealthlab.tax.foreign_tax_validation import unique

    quotes = {(q.date, q.currency): q for q in plan.quotes}
    unique([(q.date, q.currency) for q in plan.quotes], "date/currency quote")
    validate_quote_coverage(quotes, plan, scenario)
    if any(q.currency == "USD" and q.usd_per_unit != 1 for q in plan.quotes):
        raise ValueError("A USD settlement quote requires unit conversion.")


def validate_quote_coverage(quotes, plan, scenario):
    currencies = {r.currency for r in plan.assessments}
    observations = [end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)]
    if any((when, currency) not in quotes for when in observations for currency in currencies):
        raise ValueError(
            "Supply every observed month-end currency quote; stale FX is not inferred."
        )


def validate_scheduled_dates(plan, scenario):
    if any(
        not scenario.start <= r.record.value.date < scenario.end
        for r in [*plan.source_withholding, *plan.refunds]
    ):
        raise ValueError("Planned foreign withholding/refunds must lie inside this projection.")
