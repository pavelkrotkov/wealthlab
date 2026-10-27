"""Reject swapped people or opening-source mismatches before executing PR household cash."""

from datetime import date

from wealthlab.tax.jurisdiction_observation import observe
from wealthlab.tax.pr_execution_context import prepare


def validate(plan, scenario):
    people = dict(zip((m.id for m in scenario.members), ("primary", "spouse"), strict=False))
    for case in plan.cases:
        if case.pr_federal is None:
            continue
        validate_coverage(case, scenario)
        from wealthlab.tax.pr_execution_gain_household import validate as validate_gains

        validate_gains(case, scenario)
        if case.pr_federal.people != people:
            raise ValueError(
                "Prepared PR context must retain the household's actual stable people."
            )
        opening = max(scenario.start, date(case.policy.year, 1, 1))
        prepare(observe(case, opening))


def validate_coverage(case, scenario):
    plan = scenario.foreign_tax_plan
    if plan is None:
        raise ValueError(
            "Prepared PR household exclusion requires the shared country-tax cash book."
        )
    covered = any(
        a.country == "PR" and a.liability_year == case.policy.year for a in plan.assessments
    )
    if not covered:
        raise ValueError("Prepared PR household year needs explicit PR assessment coverage.")
