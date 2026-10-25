"""Leg economics retain the paid premium separately from the current model value."""

from wealthlab.household.calendar import money
from wealthlab.products.option_math import direction, units
from wealthlab.products.option_valuation import value


def leg_mark(leg, mark):
    per_unit = value(leg, mark)
    signed_value = money(direction(leg) * units(leg) * per_unit)
    pnl = signed_value - direction(leg) * units(leg) * leg.premium - leg.opening_fee
    return dict(leg_id=leg.id, date=mark.date.isoformat(), model_value=signed_value, pnl=money(pnl))
