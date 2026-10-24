"""Require complete dated household sleeves and prevent overlapping asset/tax books."""

from wealthlab.products.household_accounts import excluded_accounts, validate_account
from wealthlab.products.household_records import validate_dates, validate_records
from wealthlab.products.household_tax import validate as validate_allocations
from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario):
    plan = scenario.sleeve_plan
    if scenario.tax_plan is None:
        raise ValueError("Household sleeves require explicit household tax assumptions.")
    validate_tax(scenario.tax_plan, scenario)
    validate_scope(plan, scenario)
    accounts = {a.id: a for a in scenario.accounts}
    forbidden = excluded_accounts(scenario)
    for sleeve in plan.sleeves:
        validate_account(sleeve, accounts, forbidden)
        validate_dates(sleeve, scenario)
        validate_allocations(sleeve, scenario)


def validate_scope(plan, scenario):
    if scenario.start.day != 1 or scenario.end.day != 1:
        raise ValueError("Household sleeves require complete calendar months.")
    if not (
        plan.actual_household_cash_confirmed
        and plan.other_tax_inputs_exclude_supplied_allocations_confirmed
    ):
        raise ValueError(
            "Confirm actual household collateral cash and no duplicate sleeve tax inputs."
        )
    ids = [s.account_id for s in plan.sleeves]
    if len(ids) != len(set(ids)):
        raise ValueError("Give each sleeve a separate household account.")
    validate_records(plan)
