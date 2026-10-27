"""Missing home, lien, tax or timing facts block the bounded source-provided profile.

No residence exclusion, rental depreciation, debt forgiveness or mortgage
interest deduction is derived. Existing debt principal is never copied into a
second liability. Unsupported deductible-interest attribution remains explicit.
"""

from wealthlab.household.property_terms import (
    validate_debts,
    validate_observations,
    validate_sale,
    validate_terms,
)
from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario):
    plan = scenario.property_plan
    if scenario.tax_plan is None:
        raise ValueError("Property requires explicit independent household tax assumptions.")
    validate_tax(scenario.tax_plan, scenario)
    if not (
        plan.other_tax_inputs_exclude_property_recognition_confirmed
        and plan.debt_payoff_full_month_native_interest_confirmed
    ):
        raise ValueError(
            "Confirm excluded duplicate tax inputs and native full-month payoff interest."
        )
    validate_scope(scenario)
    validate_identity(plan)
    for holding in plan.holdings:
        validate_holding(scenario, holding)
    validate_deductions(scenario)


def validate_scope(scenario):
    validate_months(scenario)
    accounts = {a.account_id for a in scenario.property_plan.holdings}
    if accounts != {a.id for a in scenario.accounts if a.wrapper == "property"}:
        raise ValueError("Bind every native property account exactly once.")
    if any(c.destination in accounts for c in scenario.contributions):
        raise ValueError(
            "Property acquisition/improvements require another capital transaction adapter."
        )


def validate_holding(scenario, holding):
    validate_account(scenario, holding)
    validate_terms(scenario, holding)
    validate_debts(scenario, holding)
    validate_observations(scenario, holding)
    validate_sale(scenario, holding)


def validate_account(scenario, holding):
    account = next((a for a in scenario.accounts if a.id == holding.account_id), None)
    if account is None or (account.wrapper, account.currency, account.monthly_fee) != (
        "property",
        "USD",
        0,
    ):
        raise ValueError("Property needs its own USD property account with zero generic fee.")


def validate_identity(plan):
    from itertools import chain

    records = chain(
        plan.holdings,
        chain.from_iterable(h.observations for h in plan.holdings),
        (h.sale for h in plan.holdings if h.sale is not None),
    )
    unique((r.id for r in records), "source record")
    unique((h.account_id for h in plan.holdings), "property account")
    unique(chain.from_iterable(h.linked_debt_ids for h in plan.holdings), "linked debt")


def unique(items, name):
    values = list(items)
    if len(values) != len(set(values)):
        raise ValueError("Property " + name + " identifiers must be unique.")


def validate_months(scenario):
    if scenario.start.day != 1 or scenario.end.day != 1:
        raise ValueError("Property supports complete calendar months and actual month-end closes.")


def validate_deductions(scenario):
    if any(h.linked_debt_ids for h in scenario.property_plan.holdings) and any(
        c.federal_deductions.qualified_mortgage_interest for c in scenario.tax_plan.cases
    ):
        raise ValueError(
            "Linked liens need zero mortgage-interest deductions; dated attribution is unsupported."
        )
