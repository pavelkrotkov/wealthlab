"""Validate stable foreign identities and dated quotes before any cash mutation."""

from wealthlab.tax.foreign_tax_profile_validation import (
    validate_credit_ownership,
    validate_profiles,
)
from wealthlab.tax.foreign_tax_settlement_validation import validate_quotes, validate_records
from wealthlab.tax.foreign_tax_sources import validate_links


def validate(plan, scenario):
    if scenario.tax_plan is None:
        raise ValueError("Foreign cash execution requires the household's annual tax ledger.")
    assessments = {r.id: r for r in plan.assessments}
    unique([r.id for r in plan.assessments], "assessment")
    unique([r.id for r in plan.schedules], "payment schedule")
    records = cash_records(plan)
    unique([r.record.id for r in records], "tax cash")
    validate_owners(plan, scenario)
    validate_references(plan, assessments)
    validate_records(plan, assessments, scenario)
    validate_quotes(plan, scenario)
    validate_profiles(plan, scenario)
    validate_credit_ownership(plan, scenario)
    validate_links(plan, assessments)


def validate_owners(plan, scenario):
    members = {m.id for m in scenario.members}
    if any(a.owner_id not in members or a.country == "US" for a in plan.assessments):
        raise ValueError("Foreign assessments need a household owner and foreign jurisdiction.")


def validate_references(plan, assessments):
    records = cash_records(plan)
    for item in [*plan.schedules, *plan.revisions, *records]:
        if item.assessment_id not in assessments:
            raise ValueError("Each foreign payment/revision must identify a known assessment.")


def unique(values, label):
    if len(values) != len(set(values)):
        raise ValueError(f"Foreign {label} identities must be unique.")


def cash_records(plan):
    return [*plan.opening_payments, *plan.source_withholding, *plan.refunds]
