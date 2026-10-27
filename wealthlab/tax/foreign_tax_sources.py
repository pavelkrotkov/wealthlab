"""Scope source labels by stable person and recognition year without renaming payments.

Recurring source labels may survive a move or calendar reset. The lower credit
bridge uses a unique token, while this reversible audit retains each original
person/year/source tuple. Payment source-income year is explicitly supplied;
it is never inferred from a foreign liability year or from payment timing.
"""

from hashlib import sha256

from wealthlab.tax.foreign_credit_sources import SUPPORTED, reconcile


def key(owner, year, identity):
    value = f"{owner}:{year}:{identity}".encode()
    return "income_" + sha256(value).hexdigest()[:40]


def history(profiles, when=None):
    rows, identities = {}, {}
    for profile in profiles:
        for row in profile.income:
            if when is not None and row.value.date > when:
                continue
            token = key(row.owner_id, row.value.date.year, row.id)
            transformed = row.model_copy(update=dict(id=token))
            if token in rows and rows[token] != transformed:
                raise ValueError("Each person/year/source identity needs one recognized event.")
            rows[token] = transformed
            identities[token] = dict(
                owner_id=row.owner_id, recognition_year=row.value.date.year, source_id=row.id
            )
    return list(rows.values()), identities


def payment_record(item):
    record = item.record
    if record.income_ids and item.source_income_year is None:
        raise ValueError("Linked tax cash needs an explicit US source-income recognition year.")
    values = dict(
        income_ids=[
            key(record.owner_id, item.source_income_year, identity)
            for identity in record.income_ids
        ]
    )
    if record.fx_income_id is not None:
        values["fx_income_id"] = key(record.owner_id, record.value.date.year, record.fx_income_id)
    return record.model_copy(update=values)


def schedule_sources(schedule, owner):
    if schedule.income_ids and schedule.source_income_year is None:
        raise ValueError("Scheduled tax needs an explicit linked US income-recognition year.")
    return [key(owner, schedule.source_income_year, identity) for identity in schedule.income_ids]


def validate_links(plan, assessments):
    rows, _ = history(plan.credit_profiles)
    known = {row.id for row in rows}
    for schedule in plan.schedules:
        owner = assessments[schedule.assessment_id].owner_id
        validate_known(schedule_sources(schedule, owner), known)
    records = [*plan.opening_payments, *plan.source_withholding, *plan.refunds]
    for item in records:
        validate_known(payment_record(item).income_ids, known)


def validate_known(identities, known):
    if any(identity not in known for identity in identities):
        raise ValueError(
            "Each tax payment must link an explicit person/recognition-year/source row."
        )


def denied_source_reasons(case):
    if case.eligibility != "denied":
        return []
    from wealthlab.tax.pr_execution_credit_sources import extra_source_fields

    try:
        fields = SUPPORTED | extra_source_fields(case)
        if any(v for k, v in case.annual.federal_income.model_dump().items() if k not in fields):
            return [
                "Denied US credit does not establish foreign capital/retirement/business sourcing."
            ]
        reconcile(case)
    except ValueError as error:
        return [str(error)]
    if not case.ordinary_source_and_tax_allocation_confirmed:
        return ["Foreign source completeness remains unresolved despite denied US credit."]
    return []
