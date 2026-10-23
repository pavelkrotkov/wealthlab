"""Share targets and gross portfolio weights deliberately use different denominators."""

from decimal import ROUND_CEILING, ROUND_DOWN, Decimal

from wealthlab.portfolio.orders import Trade
from wealthlab.portfolio.selection import candidates

UNIT = Decimal("0.000001")


def positions(book, policy):
    security_value = sum(
        lot.quantity * policy.prices[lot.security_id]
        for lot in book.lots.values()
        if lot.security_id == policy.security_id
    )
    wealth = sum(book.cash.values()) + sum(
        lot.quantity * policy.prices[lot.security_id] for lot in book.lots.values()
    )
    return security_value, wealth


def original_lots(case, policy):
    return {
        lot.id: lot
        for lot in case.lots
        if lot.account_id == policy.account_id and lot.security_id == policy.security_id
    }


def eligible_lots(case, book, policy):
    probe = Trade(
        id=policy.id,
        provenance=policy.provenance,
        date=policy.date,
        action="sell",
        account_id=policy.account_id,
        security_id=policy.security_id,
        quantity=Decimal(1),
        price=policy.prices[policy.security_id],
        commission=policy.commission,
        selection=policy.selection,
    )
    lots = candidates(book.lots, probe)
    if policy.mode == "original_fraction":
        opening = original_lots(case, policy)
        lots = [lot for lot in lots if book.origins[lot.id] in opening]
    return lots


def requested(case, book, policy):
    """A staged fraction is cumulative, including manual sales of original shares.

    Concentration uses all configured accounts and cash, before taxes. Selling
    converts stock to cash; only the commission reduces this gross denominator.
    """
    if policy.mode == "retain":
        return Decimal(0)
    if policy.mode == "sell_all":
        return sum((lot.quantity for lot in eligible_lots(case, book, policy)), Decimal(0))
    if policy.mode == "original_fraction":
        return staged_quantity(case, book, policy)
    return concentration_quantity(book, policy)


def staged_quantity(case, book, policy):
    fraction = policy.fraction
    assert fraction is not None
    opening = original_lots(case, policy)
    original = sum(lot.quantity for lot in opening.values())
    retained = sum(lot.quantity for lot in book.lots.values() if book.origins[lot.id] in opening)
    return max(Decimal(0), original * fraction - (original - retained)).quantize(
        UNIT, rounding=ROUND_DOWN
    )


def concentration_quantity(book, policy):
    fraction = policy.fraction
    assert fraction is not None
    value, wealth = positions(book, policy)
    if value <= fraction * wealth:
        return Decimal(0)
    amount = (value - fraction * (wealth - policy.commission)) / policy.prices[policy.security_id]
    return amount.quantize(UNIT, rounding=ROUND_CEILING)
