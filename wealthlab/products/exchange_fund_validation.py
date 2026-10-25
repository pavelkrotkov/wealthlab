"""Reject overlapping capital, unknown legal assumptions and incomplete monthly marks."""

from types import SimpleNamespace

from wealthlab.products.exchange_fund_accounts import validate_account
from wealthlab.products.exchange_fund_basket_validation import validate_basket
from wealthlab.products.exchange_fund_records import allocations, validate_records
from wealthlab.products.household_tax import validate as validate_allocations
from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario):
    plan = scenario.exchange_fund_plan
    if scenario.tax_plan is None:
        raise ValueError("Exchange funds require explicit household tax assumptions.")
    validate_tax(scenario.tax_plan, scenario)
    if not (
        plan.all_terms_tax_and_basis_assumptions_confirmed
        and plan.other_tax_inputs_exclude_product_confirmed
        and plan.no_external_substantially_identical_trades_confirmed
    ):
        raise ValueError(
            "Confirm complete conditional exchange terms and nonduplicated tax inputs."
        )
    treatments = [
        plan.nj_wash_treatment,
        plan.federal_contribution,
        plan.nj_contribution,
        plan.federal_basket_distribution,
        plan.nj_basket_distribution,
    ]
    if "unconfirmed" in treatments:
        raise ValueError("Unconfirmed exchange tax treatment blocks calculation.")
    validate_account(scenario, plan)
    validate_records(scenario, plan)
    validate_basket(plan)
    validate_allocations(SimpleNamespace(allocations=allocations(plan)), scenario)
