"""Cross-person/year uniqueness and chronology without inventing residence or tax deadlines."""

from datetime import date


def unique(values, message):
    if len(set(values)) != len(values):
        raise ValueError(message)


def validate(plan):
    records = {annual.id: annual for annual in plan.annuals}
    unique([r.id for r in [*plan.annuals, *plan.obligations]], "Plan record IDs must be unique.")
    unique(
        [(a.case.person_id, a.case.year) for a in plan.annuals],
        "Only one current assessment per person and liability year is supported.",
    )
    unique(
        [p.id for a in plan.annuals for p in a.case.payments],
        "A payment ID cannot be recognized by more than one annual assessment.",
    )
    for annual in plan.annuals:
        validate_annual(plan, annual)
    for obligation in plan.obligations:
        validate_obligation(records, obligation)


def validate_obligation(records, obligation):
    annual = records.get(obligation.assessment_id)
    if annual is None:
        raise ValueError("Every scheduled obligation must identify an annual assessment.")
    if obligation.due_date.year < annual.case.year:
        raise ValueError("A scheduled obligation cannot predate its liability year.")


def validate_annual(plan, annual):
    case = annual.case
    if case.synthetic != plan.synthetic:
        raise ValueError("The plan and each annual case must agree on synthetic provenance.")
    if case.as_of > plan.as_of:
        raise ValueError("Annual observations cannot follow the plan as-of date.")
    if case.as_of < date(case.year, 12, 31):
        raise ValueError("Annual assessments require a completed calendar year of fiscal facts.")
