"""Classify household current earned payroll before deriving any work-test benefit cash."""

from datetime import date

from wealthlab.retirement.medicare_household_inputs import withholding
from wealthlab.retirement.social_work_household_wages import wage_rules
from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario):
    case = scenario.social_security
    if case is None or scenario.tax_plan is None:
        raise ValueError("Household work tests require generated claims and an annual tax plan.")
    if (scenario.start, scenario.end) != (date(case.start_year, 1, 1), date(case.end_year, 1, 1)):
        raise ValueError("Household work tests require matching complete calendar-year horizons.")
    if withholding(scenario):
        raise ValueError("Work-test benefits currently require no Medicare SSA withholding.")
    if scenario.compensation_plan is not None:
        raise ValueError("Employer allocation wages require separate earned-month classification.")
    if any(r.actual_monthly_wages is not None for r in scenario.social_work_plan.years):
        raise ValueError(
            "Leave household actual work wages unset; actual gross payroll supplies them."
        )
    validate_tax(scenario.tax_plan, scenario)
    validate_opening(scenario.tax_plan)
    wage_rules(scenario)


def validate_opening(plan):
    incomes = [c.federal_income for c in plan.cases] + [e.federal for e in plan.events]
    if any(i.wages_primary or i.wages_spouse for i in incomes):
        raise ValueError(
            "Manual/opening W2 amounts need earned-month classification for work tests."
        )
