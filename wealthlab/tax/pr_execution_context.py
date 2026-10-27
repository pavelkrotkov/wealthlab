"""Prepare the existing PR policy without recursively evaluating its baseline.

Worldwide source facts stay in the annual record. Only receipts through the
observation date enter the existing residence/exclusion calculation. Each
source retains its actual person, role and calendar year; a favorable BFR
claim cannot substitute for missing ownership or source evidence.
"""

from datetime import date, timedelta

from wealthlab.tax.pr_facts import PRCase
from wealthlab.tax.pr_guards import guards
from wealthlab.tax.pr_inputs import validate
from wealthlab.tax.pr_residence import federal_status


def prepare(annual):
    context = annual.pr_federal
    validate_context(context, annual)
    rows = [r.income for r in context.sources if r.income.received <= context.as_of]
    case = PRCase(
        baseline=annual.model_copy(update=dict(pr_federal=None)),
        primary=context.primary,
        spouse=context.spouse,
        income=rows,
        pr_regime=context.pr_regime,
        pr_wages_reported_on_form_499r2=context.pr_wages_reported_on_form_499r2,
        pr_allowed_deductions=context.pr_allowed_deductions,
        pr_abt_allowed_deductions=context.pr_abt_allowed_deductions,
        description=context.source,
    )
    validate(case)
    statuses = {
        role: federal_status(getattr(case, role), annual.policy.year)
        for role in context.people.values()
    }
    reasons = guards(case, allow_gains=context.gain_profile is not None)
    reasons += [r for status in statuses.values() for r in status["reasons"]]
    if reasons:
        raise ValueError("; ".join(reasons))
    return case, statuses


def validate_context(context, annual):
    year = annual.policy.year
    if not date(year, 1, 1) - timedelta(days=1) <= context.as_of <= date(year, 12, 31):
        raise ValueError("Prepared PR context must observe its actual federal calendar year.")
    required = {"primary", "spouse"} if annual.filing.status == "joint" else {"primary"}
    if set(context.people.values()) != required or len(context.people) != len(required):
        raise ValueError("Prepared PR people must match the actual federal filing unit.")
    identities = [(r.owner_id, r.id) for r in context.sources]
    if len(identities) != len(set(identities)):
        raise ValueError("Prepared PR person/year/source identities must be unique.")
    for source in context.sources:
        validate_source(source, context, year)


def validate_source(source, context, year):
    if context.people.get(source.owner_id) != source.income.owner:
        raise ValueError("Prepared PR source owner must retain the actual stable person/role.")
    if source.income.received.year != year or not source.classification_assumed_confirmed:
        raise ValueError(
            "Prepared PR source date and independent classifications need confirmation."
        )
    if not source.income.evidence.strip():
        raise ValueError("Prepared PR source classification needs its own evidence.")
