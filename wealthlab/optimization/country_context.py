"""One source-backed country context is fixed across every choice and realized path."""

from datetime import timedelta

from wealthlab.tax.country_wages import validate as validate_wages
from wealthlab.tax.jurisdiction_execution import MAX_PASSES
from wealthlab.tax.spain_cash_sources import validate as validate_cash


def validate(case):
    context, household = case.country_context, case.household
    if context is None:
        if household.foreign_tax_plan is not None:
            raise ValueError("Foreign-tax search requires an explicit fixed country context.")
        return
    if household.tax_plan is None or household.foreign_tax_plan is None:
        raise ValueError("A fixed country context needs the original domestic and foreign books.")
    if context.spain is None and not any(c.pr_federal for c in household.tax_plan.cases):
        raise ValueError("Provide the native PR profile or complete fixed Spain execution facts.")
    validate_source(context, household)
    validate_wages(household, context)
    validate_cash(household, context.spain, context.cash_sources)


def validate_source(context, household):
    if (
        not context.source.strip()
        or not context.all_candidate_income_market_and_fiscal_facts_confirmed
        or (context.wage_sources and not context.replace_bound_future_wages_confirmed)
        or context.source_date > household.start
        or context.valid_through < household.end - timedelta(days=1)
    ):
        raise ValueError("Confirm dated country source facts valid for every candidate and path.")


def projection_passes(case):
    return MAX_PASSES if case.country_context is not None else 1
