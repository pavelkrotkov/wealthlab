"""Target dollars are fixed from current shares, before this decision's costs.

Weights describe this account's securities, excluding cash and other accounts.
Cash already in the book is reserved for the normal household sweep. A policy
can reinvest only its own net sale receipts, with no wallet top-up or leverage.
"""

from decimal import Decimal

ZERO = Decimal(0)


def values(book, policy, prices):
    holdings = {key: ZERO for key in policy.target_weights}
    for lot in book.lots.values():
        if lot.account_id == policy.account_id:
            holdings[lot.security_id] += lot.quantity * prices[lot.security_id]
    return holdings


def weights(holdings):
    total = sum(holdings.values(), ZERO)
    return {key: value / total if total else ZERO for key, value in holdings.items()}


def liquid_units(book, policy, security):
    return sum(
        (
            lot.quantity
            for lot in book.lots.values()
            if lot.account_id == policy.account_id
            and lot.security_id == security
            and lot.acquired <= policy.date
            and lot.liquid_after <= policy.date
        ),
        ZERO,
    )


def snapshot(book, policy, prices):
    before = values(book, policy, prices)
    total = sum(before.values(), ZERO)
    return dict(
        before=before,
        total=total,
        weights=weights(before),
        targets={key: weight * total for key, weight in policy.target_weights.items()},
        cash=book.cash[policy.account_id],
        history=len(book.history),
    )


def report(book, policy, prices, state, status, locked):
    after = values(book, policy, prices)
    current = weights(after)
    trades = book.history[state["history"] :]
    return dict(
        policy=policy.id,
        date=policy.date.isoformat(),
        account_id=policy.account_id,
        status=status,
        opening_security_value=state["total"],
        gross_sales=sum((t.quantity * t.price for t in trades if t.action == "sell"), ZERO),
        gross_purchases=sum((t.quantity * t.price for t in trades if t.action == "buy"), ZERO),
        commissions=sum((t.commission for t in trades), ZERO),
        residual_cash=book.cash[policy.account_id] - state["cash"],
        trade_ids=[t.id for t in trades],
        securities=[
            dict(
                security_id=key,
                target_weight=policy.target_weights[key],
                weight_before=state["weights"][key],
                weight_after=current[key],
                target_value_before_costs=state["targets"][key],
                value_after=after[key],
                remaining_target_value=state["targets"][key] - after[key],
                market_locked=key in locked,
                liquid_units_remaining=liquid_units(book, policy, key),
            )
            for key in sorted(after)
        ],
    )
