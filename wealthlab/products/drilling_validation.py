"""Unknown legal/tax assumptions and overlapping capital cannot become favorable defaults."""

from datetime import timedelta

from wealthlab.household.calendar import months
from wealthlab.products.drilling_accounts import validate_account
from wealthlab.products.drilling_records import validate_records, validate_tax
from wealthlab.tax.projection_validation import validate as validate_household_tax


def validate(scenario):
    plan = scenario.drilling_plan
    if scenario.tax_plan is None:
        raise ValueError("Drilling requires an explicit household tax plan.")
    validate_household_tax(scenario.tax_plan, scenario)
    choices = (
        plan.legal_form,
        plan.federal_ordinary,
        plan.se_classification,
        plan.nj_exit_category,
        plan.reference_nj_wash_treatment,
    )
    if "unconfirmed" in choices:
        raise ValueError(
            "Resolve drilling legal form, income classification and reference assumptions."
        )
    confirmations = (
        plan.working_interest_eligibility_supplied_confirmed,
        plan.supplied_qbi_amt_history_and_limits_confirmed,
        plan.all_cash_basis_terms_and_recognition_complete_confirmed,
        plan.paid_operating_costs_deductible_assumption_confirmed,
        plan.other_tax_inputs_exclude_product_confirmed,
        plan.unmodeled_liability_risk_acknowledged,
        plan.reference_zero_fees_and_no_external_identical_trades_confirmed,
    )
    if not all(confirmations):
        raise ValueError(
            "Confirm supplied drilling terms, prelimited tax facts and unresolved liability risk."
        )
    validate_account(scenario, plan)
    validate_dates(scenario, plan)
    validate_records(plan)
    validate_tax(scenario, plan)


def validate_dates(scenario, plan):
    ends = [end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)]
    if (
        scenario.start.day != 1
        or scenario.end.day != 1
        or [o.date for o in plan.observations] != ends
    ):
        raise ValueError("Drilling observations must cover every complete household month end.")
