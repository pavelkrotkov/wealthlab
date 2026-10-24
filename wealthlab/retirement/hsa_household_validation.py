"""Household HSA years share actual cash, accounts and a single receipt history.

Coverage forecasts must match the household members and confirmed Medicare
coverage. Annual contexts have no independent opening balances or receipts;
the current wallet supplies the HSA book at each year boundary.
"""

from wealthlab.retirement.hsa_household_coverage import validate_medicare
from wealthlab.retirement.hsa_household_sources import validate_sources
from wealthlab.retirement.hsa_inputs import HSACase
from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario):
    plan = scenario.hsa_plan
    if scenario.tax_plan is None:
        raise ValueError("Household HSA funding requires explicit household taxes.")
    validate_tax(scenario.tax_plan, scenario)
    if not all(
        (
            plan.conditional_nj_treatment_confirmed,
            plan.cash_only_accounts_and_complete_context_confirmed,
            plan.receipts_paid_before_projection_confirmed,
            plan.employer_funding_excluded_from_other_nj_wages_confirmed,
        )
    ):
        raise ValueError(
            "Confirm complete cash HSAs, conditional NJ treatment, prior paid receipts "
            "and no duplicate employer wages."
        )
    if (scenario.start.month, scenario.start.day, scenario.end.month, scenario.end.day) != (
        1,
        1,
        1,
        1,
    ):
        raise ValueError("This household HSA profile requires complete calendar years.")
    if sorted(y.year for y in plan.years) != list(range(scenario.start.year, scenario.end.year)):
        raise ValueError("Provide one HSA eligibility context for every household year.")
    validate_sources(scenario)
    validate_establishment_history(plan.years)
    for context in plan.years:
        validate_year(scenario, context)


def validate_year(scenario, context):
    if {p.id: p.birth_date for p in context.owners} != {
        p.id: p.birth_date for p in scenario.members
    }:
        raise ValueError("HSA eligibility members and births must match the household.")
    if context.married != (len(scenario.members) == 2):
        raise ValueError("HSA married limits must match the household filing unit.")
    accounts = [a for a in scenario.accounts if a.wrapper == "hsa"]
    annual_case(scenario.hsa_plan, context, accounts)
    validate_medicare(scenario, context)


def annual_case(plan, context, accounts):
    def events(rows):
        return [r for r in rows if r.date.year == context.year]

    return HSACase.model_validate(
        dict(
            **context.model_dump(),
            opening_cash=0,
            complete_context=True,
            contribution_policy="monthly_only",
            nj_treatment=plan.nj_treatment,
            accounts=accounts,
            medical_receipts=plan.medical_receipts,
            contributions=events(plan.contributions),
            withdrawals=events(plan.withdrawals),
            interest=events(plan.interest),
        )
    )


def validate_establishment_history(years):
    first = {p.id: p.established for p in years[0].owners}
    if any({p.id: p.established for p in y.owners} != first for y in years):
        raise ValueError("HSA establishment history must remain consistent across household years.")
