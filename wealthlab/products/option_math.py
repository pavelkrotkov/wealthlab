"""Unit-safe payoff primitives shared by cash, valuation and share delivery."""

from decimal import Decimal


def units(leg):
    return Decimal(leg.contracts * leg.multiplier)


def direction(leg):
    return Decimal(1 if leg.side == "long" else -1)


def intrinsic(leg, spot):
    signed = spot - leg.strike if leg.kind == "call" else leg.strike - spot
    return max(Decimal(0), signed)
