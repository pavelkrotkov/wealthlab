"""Known issuer positions and account-factor proxies are different coverage measures.

A whole-account proxy gives an economic factor exposure, not an inventory of
its underlying issuers. Missing issuer holdings must not become a zero-risk
concentration observation. Cash and fully depleted accounts need no such
inventory; unbound positive noncash accounts remain visibly unmeasured.
"""

from decimal import Decimal

ZERO = Decimal(0)


def securities(lots):
    if lots is None:
        return {}
    return {
        identity: sum(
            (
                lot.quantity * lots.prices[identity]
                for lot in lots.book.lots.values()
                if lot.security_id == identity
            ),
            ZERO,
        )
        for identity in lots.book.securities
    }


def report(scenario, binding, lots, row):
    values = securities(lots)
    known = set(lots.book.accounts) if lots else set()
    unmapped_issuers = missing(scenario, row, known)
    assets = sum(row["account_balances"].values(), ZERO)
    factors = factor_values(binding, values, row)
    mapped = known | {w.account_id for w in binding.wrappers}
    return dict(
        market_security_values=values,
        market_max_security_weight=issuer_weight(values, assets, unmapped_issuers),
        market_issuer_concentration_complete=not unmapped_issuers,
        market_unmeasured_issuer_accounts=unmapped_issuers,
        market_factor_values=factors,
        market_unmapped_factor_accounts=missing(scenario, row, mapped),
    )


def missing(scenario, row, measured):
    return [
        a.id
        for a in scenario.accounts
        if a.wrapper != "cash" and a.id not in measured and row["account_balances"][a.id] > 0
    ]


def issuer_weight(values, assets, missing_accounts):
    if not values and missing_accounts:
        return None
    return max(values.values(), default=ZERO) / assets if assets else ZERO


def factor_values(binding, values, row):
    factors = {}
    for security in binding.securities:
        factors[security.factor] = factors.get(security.factor, ZERO) + values[security.security_id]
    for wrapper in binding.wrappers:
        factors[wrapper.factor] = (
            factors.get(wrapper.factor, ZERO) + row["account_balances"][wrapper.account_id]
        )
    return factors
