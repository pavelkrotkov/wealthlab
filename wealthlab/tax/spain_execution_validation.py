"""Country identities and tax-credit policy are checked before the shared wallet runs.

Each person/year has three distinct native levies. Cash bindings preserve the
observed date, currency and tax kind; an IRPF observation cannot pay wealth
tax or enter a different spouse's US credit. Unknown bilateral relief is
withheld before any favorable cash execution can be returned.
"""

from datetime import timedelta

from wealthlab.tax.spain_assessment_plan import TAXES, evaluate_plan
from wealthlab.tax.spain_execution_sources import validate_sources


def validate(scenario, execution):
    if not execution.us_source_and_spanish_recognition_reconciled_confirmed:
        raise ValueError("Independent US and Spanish source/recognition facts need reconciliation.")
    if execution.spanish_foreign_credit_treatment != "denied":
        raise ValueError("Spain paid-US-tax/treaty credit allocation remains unresolved.")
    evaluate_plan(execution.assessments)
    validate_sources(scenario, execution)
    validate_bindings(execution)
    foreign = {a.id: a for a in scenario.foreign_tax_plan.assessments}
    annuals = {a.id: a.case for a in execution.assessments.annuals}
    for binding in execution.bindings:
        validate_binding(scenario, annuals[binding.annual_id], binding, foreign)


def validate_binding(scenario, annual, binding, foreign):
    target = foreign.get(binding.foreign_assessment_id)
    kind = "income" if binding.tax_type == "irpf" else "wealth"
    expected = (annual.person_id, "ES", annual.year, kind, "EUR", annual.as_of)
    if (
        target is None
        or (
            target.owner_id,
            target.country,
            target.liability_year,
            target.tax_type,
            target.currency,
            target.observed,
        )
        != expected
    ):
        raise ValueError(
            "Spain binding must preserve person/year/tax/currency/observation identity."
        )
    if annual.as_of > scenario.end - timedelta(days=1):
        raise ValueError("Spain country assessment cannot occur after the household horizon.")
    if any(annual.credits.model_dump()[k] for k in ("irpf_state", "irpf_regional")):
        raise ValueError("Denied Spain foreign credit cannot retain a supplied IRPF credit.")


def validate_bindings(execution):
    expected = {(a.id, tax) for a in execution.assessments.annuals for tax in TAXES}
    actual = {(b.annual_id, b.tax_type) for b in execution.bindings}
    ids = [b.foreign_assessment_id for b in execution.bindings]
    if actual != expected or len(ids) != len(set(ids)) or len(ids) != len(expected):
        raise ValueError(
            "Every native Spain tax needs one distinct stable cash assessment binding."
        )
