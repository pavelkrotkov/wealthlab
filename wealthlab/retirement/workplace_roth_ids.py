"""Internal RMD identities cannot alias a supplied Roth cash event in the shared workplace book."""

from wealthlab.retirement.workplace_rmd_validation import PREFIX


def validate_ids(cash, plan):
    records = [*cash.orders, *plan.orders, *plan.returns, *plan.liquidity_locks]
    if plan.cash_withdrawals is not None:
        records += [*plan.cash_withdrawals.orders, *plan.cash_withdrawals.direct_rollovers]
    if any(o.id.startswith(PREFIX) for o in cash.orders):
        raise ValueError("The automatic RMD event prefix is reserved for internal orders.")
    ids = [r.id for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Roth and pretax workplace event IDs must be unique.")
