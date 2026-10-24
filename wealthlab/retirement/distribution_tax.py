"""Matched annual liabilities use the existing filing engine; no tax cash is invented."""

from decimal import Decimal

from wealthlab.tax.annual import evaluate


def compare(case, rows):
    annual = case.annual_tax_case
    if annual is None:
        return None
    taxable = sum((row["federal_taxable"] for row in rows), Decimal(0))
    penalty = sum((row["additional_tax"] for row in rows), Decimal(0))
    nj_taxable = sum((row["nj_taxable"] for row in rows), Decimal(0))
    eligible = pension_eligible(case, rows)
    federal = annual.federal_income.model_copy(
        update=dict(
            ira_distributions=annual.federal_income.ira_distributions + taxable,
            retirement_additional_tax=annual.federal_income.retirement_additional_tax + penalty,
        )
    )
    retirement = annual.nj_income.retirement.model_copy(
        update=dict(qualified_pension=annual.nj_income.retirement.qualified_pension + eligible)
    )
    nj = annual.nj_income.model_copy(
        update=dict(pension=annual.nj_income.pension + nj_taxable, retirement=retirement)
    )
    updated = annual.model_copy(update=dict(federal_income=federal, nj_income=nj))
    baseline, modeled = evaluate(annual), evaluate(updated)
    return dict(
        without_distributions=baseline,
        with_distributions=modeled,
        additional_liability=modeled["total_liability"] - baseline["total_liability"],
    )


def pension_eligible(case, rows):
    """Age-62 pension exclusion eligibility is owner-specific, not household-wide.

    Disability eligibility for a younger owner is outside this initial layer;
    no spouse's eligible age can grant it to another person's distributions.
    """
    owners = {p.id for p in case.owners if case.year - p.birth_date.year >= 62}
    return sum((row["nj_taxable"] for row in rows if row["owner"] in owners), Decimal(0))
