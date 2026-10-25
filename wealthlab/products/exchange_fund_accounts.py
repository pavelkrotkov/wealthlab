"""One actual source account owns the shares; exclude every competing capital book.

The no-external-identical-trade declaration bounds loss recognition. A known
shared wash group in another actual lot book contradicts that declaration and
must block calculation, even when the accounts themselves are different.
The account cannot also fund generic withdrawals against a stale second basis.
"""

from wealthlab.household.calendar import money
from wealthlab.products.option_exchange_accounts import validate as validate_product_ownership


def validate_account(scenario, plan):
    account = next((a for a in scenario.accounts if a.id == plan.account_id), None)
    if account is None or (account.wrapper, account.currency, account.monthly_fee) != (
        "taxable",
        "USD",
        0,
    ):
        raise ValueError("Exchange account must be a known USD taxable account without other fees.")
    validate_exclusions(scenario, plan)
    validate_source(scenario, plan, account)
    validate_wash_scope(scenario, plan)


def validate_source(scenario, plan, account):
    lot = plan.source_lot
    if lot.account_id != account.id or lot.security_id != plan.source_security.id:
        raise ValueError("Contribution lot must belong to the source account and security.")
    if lot.acquired > scenario.start or (
        plan.contribution_quantity and lot.liquid_after > scenario.start
    ):
        raise ValueError("Contribution shares must be acquired and available at opening.")
    if plan.contribution_quantity > lot.quantity:
        raise ValueError("Contribution exceeds actual source shares.")
    if money(lot.quantity * plan.opening_prices[lot.security_id]) != account.balance:
        raise ValueError("Exchange opening account must reconcile to actual source shares.")


def validate_exclusions(scenario, plan):
    validate_product_ownership(scenario)
    blocked = {c.destination for c in scenario.contributions}
    blocked |= {s.account_id for s in scenario.tax_plan.funding_sources}
    blocked |= {a.id for a in scenario.lot_plan.case.accounts} if scenario.lot_plan else set()
    blocked |= (
        {s.account_id for s in scenario.sleeve_plan.sleeves} if scenario.sleeve_plan else set()
    )
    if plan.account_id in blocked:
        raise ValueError("Exchange account cannot share another product, lot or funding book.")


def validate_wash_scope(scenario, plan):
    if scenario.lot_plan is None:
        return
    groups = {s.wash_group for s in scenario.lot_plan.case.securities}
    product_groups = {
        plan.source_security.wash_group,
        *(b.security.wash_group for b in plan.basket),
    }
    if groups & product_groups:
        raise ValueError(
            "Exchange no-external-trade profile cannot overlap another lot wash group."
        )
