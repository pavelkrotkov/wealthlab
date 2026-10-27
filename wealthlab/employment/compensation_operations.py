"""Economic changes conserve tranche value except for grants, market changes and forfeitures."""

from decimal import Decimal

from wealthlab.household.calendar import money


def grant(state, event, tranche):
    state["unvested"] += event.amount
    return Decimal(0)


def net_return(state, event, tranche):
    for bucket in ("vested", "unvested"):
        state[bucket] = money(state[bucket] * (1 + event.rate))
    return Decimal(0)


def vest(state, event, tranche):
    amount = available(state["unvested"], event.amount)
    state["unvested"] -= amount
    state["vested"] += amount
    return Decimal(0)


def forfeit(state, event, tranche):
    state["unvested"] -= available(state["unvested"], event.amount)
    return Decimal(0)


def distribution(state, event, tranche):
    if event.election == "retain" or not cash_right(event, tranche):
        return Decimal(0)
    amount = min(state[event.bucket], event.amount)
    state[event.bucket] -= amount
    return amount


def cash_right(event, tranche):
    tax = event.purpose == "tax_distribution"
    if event.bucket == "unvested":
        return tax and tranche.unvested_tax_cash_right_confirmed
    return event.date >= tranche.liquid_from or (
        tax and tranche.vested_tax_cash_before_liquidity_confirmed
    )


def available(balance, requested):
    # None means the whole remaining vesting slice, so returns and prior
    # forfeiture cannot make an unchanged full-vesting request invent assets.
    return balance if requested is None else min(balance, requested)


def termination(state, event, tranche):
    # Legal/source facts cannot manufacture economic settlement or cash.
    return Decimal(0)


OPERATIONS = dict(
    grant=grant,
    net_return=net_return,
    vest=vest,
    forfeit=forfeit,
    distribution=distribution,
    termination=termination,
)
