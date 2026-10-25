"""RMD groups cover complete distinct plans, never inferred account-name groupings.

Each group has one owner, an explicitly eligible beneficiary table and complete
pretax balances. Current-employer delays and pre-separation in-service access
require their own profiles; ordinary cash must be available by December 1.
"""

from wealthlab.retirement.workplace_rmd_eligibility import validate_group

PREFIX = "wlrmd_auto_"


def validate(scenario):
    cash = scenario.workplace_plan.cash_withdrawals
    config = cash.rmd
    if config is None:
        if not cash.orders:
            raise ValueError("Provide workplace cash orders or an explicit RMD policy.")
        return
    if not config.no_unmodeled_opening_shortfalls_confirmed:
        raise ValueError("Confirm no unmodeled opening RMD shortfalls.")
    validate_coverage(cash, scenario.workplace_plan.products)
    validate_ids(cash, scenario.workplace_plan)
    validate_owner_choices(cash, scenario)
    for group in config.groups.values():
        validate_group(group, cash, scenario)
    for order in cash.orders:
        if config.noneligible_federal_withholding_rate + order.nj_withholding_rate > 1:
            raise ValueError("RMD and NJ withholding cannot exceed gross cash.")


def validate_coverage(cash, products):
    sources = [s for group in cash.rmd.groups.values() for s in group.sources]
    pretax = {s for s, product in products.items() if product == "pretax_401k"}
    if len(sources) != len(set(sources)) or set(sources) != pretax or set(cash.profiles) != pretax:
        raise ValueError("RMD groups must cover each complete pretax source exactly once.")


def validate_ids(cash, plan):
    records = [*cash.orders, *plan.orders, *plan.returns, *plan.liquidity_locks]
    if any(r.id.startswith(PREFIX) for r in records):
        raise ValueError("Workplace RMD automatic-order ID prefix is reserved.")


def validate_owner_choices(cash, scenario):
    accounts = {a.id: a for a in scenario.accounts}
    seen = {}
    for source, profile in cash.profiles.items():
        owner = accounts[source].owner
        choice = profile.birth_1959_start_age
        if owner in seen and seen[owner] != choice:
            raise ValueError("One owner cannot use conflicting RMD start ages across plans.")
        seen[owner] = choice
