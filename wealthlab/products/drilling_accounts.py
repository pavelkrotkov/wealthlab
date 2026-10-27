"""A drilling interest owns its complete account and cannot duplicate another funding/basis book."""

from wealthlab.products.drilling_option_accounts import validate as validate_options
from wealthlab.products.household_accounts import excluded_accounts as funding_accounts


def validate_account(scenario, plan):
    validate_options(scenario)
    account = next((a for a in scenario.accounts if a.id == plan.account_id), None)
    if account is None or (account.wrapper, account.currency, account.monthly_fee) != (
        "taxable",
        "USD",
        0,
    ):
        raise ValueError(
            "Drilling needs a known USD taxable account without duplicate generic fees."
        )
    if account.balance != plan.opening_cash + plan.opening_property_value:
        raise ValueError("Drilling opening cash/property must reconcile to the household account.")
    if plan.account_id in excluded_accounts(scenario):
        raise ValueError("Drilling cannot share another product or taxable funding book.")


def excluded_accounts(scenario):
    blocked = funding_accounts(scenario)
    blocked |= (
        {s.account_id for s in scenario.sleeve_plan.sleeves} if scenario.sleeve_plan else set()
    )
    if scenario.exchange_fund_plan:
        blocked.add(scenario.exchange_fund_plan.account_id)
    if scenario.qoz_plan:
        blocked.add(scenario.qoz_plan.account_id)
    return blocked
