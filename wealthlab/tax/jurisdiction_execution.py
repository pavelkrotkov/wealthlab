"""Reconcile native country assessments through the existing single cash execution.

Reciprocal paid-tax credits can change the other country's bill. Each bounded
pass starts a fresh copy of the same household and shared wallet; only the
converged pass is returned. Actual schedules, receipts and capital never change
between passes. Nonconvergence cannot produce a favorable ranked result.
"""

from wealthlab.household.projection import project
from wealthlab.tax.jurisdiction_execution_pr import assessments as pr_assessments
from wealthlab.tax.spain_execution import assessments as spain_assessments


def evaluate(scenario, *, spain=None, max_passes=16):
    if scenario.tax_plan is None or scenario.foreign_tax_plan is None:
        raise ValueError("Country execution requires the existing domestic and foreign tax books.")
    if spain is None and not any(c.pr_federal is not None for c in scenario.tax_plan.cases):
        raise ValueError("This country execution requires a native jurisdiction assessment.")
    amounts, _ = country_assessments(scenario, spain)
    history = []
    for _ in range(max_passes):
        candidate = with_assessments(scenario, amounts)
        observed = []
        rows = project(candidate, tax_observer=observed.append)
        revised, audit = country_assessments(candidate, spain, observed)
        history.append(dict(assessments=amounts, revised_assessments=revised))
        if revised == amounts:
            return dict(
                rows=rows,
                scenario=candidate.model_dump(mode="json"),
                country_assessments=audit,
                reconciliation=history,
                status="conditional; native ordinary country facts and actual paid-tax positions",
            )
        amounts = revised
    raise ValueError("Reciprocal country-tax assessments did not converge; no result is accepted.")


def with_assessments(scenario, amounts):
    plan = scenario.foreign_tax_plan
    if any(r.assessment_id in amounts for r in plan.revisions):
        raise ValueError(
            "Native country assessments cannot also have conflicting supplied revisions."
        )
    assessments = [
        a.model_copy(update=dict(amount_native=amounts[a.id])) if a.id in amounts else a
        for a in plan.assessments
    ]
    return scenario.model_copy(
        update=dict(foreign_tax_plan=plan.model_copy(update=dict(assessments=assessments)))
    )


def country_assessments(scenario, spain, observed=None):
    pr_amounts, pr_audit = pr_assessments(scenario, observed)
    latest = observed[-1] if observed is not None else None
    es_amounts, es_audit = spain_assessments(scenario, spain, latest)
    return pr_amounts | es_amounts, pr_audit | es_audit
