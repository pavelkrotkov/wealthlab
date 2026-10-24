"""Split units and every basis together, retaining rounding residuals on the remaining lot."""

from wealthlab.household.calendar import money

BASES = ("federal_basis", "nj_basis", "economic_basis")


def split(lot, quantity):
    fraction = quantity / lot.quantity
    taken = {}
    remaining = {}
    for field in BASES:
        value = getattr(lot, field)
        amount = money(value * fraction) if value is not None else None
        taken[field] = amount
        remaining[field] = value - amount if amount is not None else None
    return (
        lot.model_copy(update=dict(quantity=quantity, **taken)),
        lot.model_copy(update=dict(quantity=lot.quantity - quantity, **remaining)),
    )
