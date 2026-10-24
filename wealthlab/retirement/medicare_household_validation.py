"""Keep prior return facts distinct from generated household income and premium cash.

Only pre-projection returns can be supplied. Later lookbacks must come from
completed annual taxes, so a static low-income forecast cannot override a
modeled conversion. Direct billing excludes the separate SSA withholding and
SMI rounding rules until their own adapter is implemented.
"""

from datetime import date

from wealthlab.retirement.medicare_enrollment import validate_income_coverage
from wealthlab.retirement.medicare_household_inputs import withholding
from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario):
    if scenario.tax_plan is None:
        raise ValueError("Household Medicare requires an explicit tax plan.")
    validate_tax(scenario.tax_plan, scenario)
    validate_collection(scenario)
    validate_context(scenario)
    validate_sources(scenario)
    validate_history(scenario)
    validate_prior_lookbacks(scenario)


def validate_sources(scenario):
    case = scenario.medicare_plan.case
    if case.income_policy != "household_completed_returns":
        raise ValueError("Select completed household returns for Medicare income.")
    if case.opening_cash or case.receipts:
        raise ValueError("Medicare uses household cash; remove standalone cash and receipts.")
    validate_benefits(scenario)


def validate_history(scenario):
    case = scenario.medicare_plan.case
    records = [*case.members, *case.coverage, *case.income_history, *case.determinations]
    if any(i.id.startswith("household_return_") for i in records):
        raise ValueError("The household_return_ prefix is reserved for generated income history.")
    if any(i.year >= scenario.start.year for i in case.income_history):
        raise ValueError(
            "Supply only pre-projection Medicare history; "
            "later income comes from completed household taxes."
        )
    if any(d.method != "three_year_fallback_confirmed" for d in case.determinations):
        raise ValueError(
            "Conditional current-income redeterminations need "
            "the standalone Medicare workbench for now."
        )


def validate_context(scenario):
    plan = scenario.medicare_plan
    if (scenario.start.month, scenario.start.day, scenario.end.month, scenario.end.day) != (
        1,
        1,
        1,
        1,
    ):
        raise ValueError("This Medicare household bridge requires complete calendar years.")
    case = plan.case
    if (case.start_year, case.end_year) != (scenario.start.year, scenario.end.year):
        raise ValueError("Medicare case years must match the household projection.")
    if {p.id for p in case.members} != {p.id for p in scenario.members}:
        raise ValueError("Medicare members must match the household members.")
    if any(c.filing.status == "separate" for c in scenario.tax_plan.cases):
        raise ValueError(
            "Separate-return Medicare residency status needs another household bridge."
        )


def validate_benefits(scenario):
    if withholding(scenario):
        if scenario.social_security is None:
            raise ValueError("SSA premium collection requires generated household claims.")
        return
    validate_no_manual_benefits(scenario)


def validate_prior_lookbacks(scenario):
    case = scenario.medicare_plan.case
    cutoff = date(min(case.end_year, case.start_year + 2), 1, 1)
    early = [
        c.model_copy(update=dict(end=min(c.end, cutoff))) for c in case.coverage if c.start < cutoff
    ]
    validate_income_coverage(case.model_copy(update=dict(coverage=early)))


def validate_collection(scenario):
    plan = scenario.medicare_plan
    if not (
        plan.costs_excluded_from_other_expenses_confirmed
        and plan.complete_household_tax_history_confirmed
    ):
        raise ValueError(
            "Confirm direct billing or SSA collection, complete history and no duplicated costs."
        )
    if withholding(scenario):
        if not plan.ssa_current_premiums_context_confirmed:
            raise ValueError(
                "Confirm standard current-premium SSA collection with one payment per recipient, "
                "no prior premium "
                "credits, arrears or other deductions."
            )
    elif not plan.direct_billing_without_benefit_withholding_confirmed:
        raise ValueError("Confirm direct Medicare billing without benefit withholding.")


def validate_no_manual_benefits(scenario):
    manual = [c.federal_income.social_security for c in scenario.tax_plan.cases]
    manual += [e.federal.social_security for e in scenario.tax_plan.events]
    rules = [r.federal for r in scenario.tax_plan.income_rules]
    if scenario.social_security is not None or any(manual) or "social_security" in rules:
        raise ValueError(
            "Benefit withholding requires the later Medicare/Social Security bridge; "
            "use direct-billed periods here."
        )
