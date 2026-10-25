"""Require complete source observations and supplied corporation tax/contract assumptions.

These checks do not establish legal qualification. They prevent a second owner
for the same household capital, unknown dividend classification, unobserved
statutory FMV and a subscription that would need a pending-investment adapter.
"""

from datetime import timedelta

from wealthlab.household.calendar import months
from wealthlab.products.qoz_accounts import validate_account
from wealthlab.products.qoz_dates import validate_dates


def validate(scenario, lots, tax):
    plan = scenario.qoz_plan
    if lots is None or tax is None:
        raise ValueError("QOZ requires an actual linked-lot source and explicit annual taxes.")
    confirmations = (
        plan.new_jersey_regime_and_basis_assumed_confirmed,
        plan.unrelated_direct_gains_no_other_elections_assumed_confirmed,
        plan.nonqualified_ep_dividends_no_extraordinary_distributions_assumed_confirmed,
        plan.limited_liability_internal_debt_only_assumed_confirmed,
        plan.calls_are_optional_partial_subscriptions_assumed_confirmed,
        plan.nav_priced_common_stock_retarget_on_calls_assumed_confirmed,
        plan.subscriptions_share_same_day_dividends_assumed_confirmed,
        plan.entity_tax_already_in_returns_assumed_confirmed,
        plan.source_and_product_tax_excluded_elsewhere_assumed_confirmed,
    )
    if not all(confirmations) or "unconfirmed" in (plan.federal, plan.new_jersey):
        raise ValueError(
            "Confirm independent QOZ tax profiles, entity tax and contract assumptions."
        )
    validate_account(scenario, plan)
    validate_economics(plan.economics)
    expected = [end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)]
    validate_observations(plan, expected)
    validate_dates(scenario, plan, expected)


def validate_observations(plan, expected):
    if [o.date for o in plan.observations] != expected:
        raise ValueError("QOZ requires ordered complete month-end observations.")
    locked = {o.date for o in plan.observations if o.locked}
    if any(c.date in locked for c in plan.calls):
        raise ValueError("Subscriptions during a market lock require a pending-investment profile.")


def validate_economics(case):
    if not case.terms_confirmed or case.outside_cash or case.short_multiple or case.redemptions:
        raise ValueError(
            "QOZ reuses confirmed long-only economics without outside cash/redemptions."
        )
    if (
        case.rebalance != "none"
        or case.margin_policy != "liquidate_on_breach"
        or case.exit_at_horizon
    ):
        raise ValueError("QOZ uses no rebalancing/top-ups or automatic horizon exit.")
