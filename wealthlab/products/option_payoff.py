"""An explicit voluntary physical exercise can have negative exercise value."""

from decimal import Decimal

from wealthlab.products.option_math import intrinsic
from wealthlab.products.option_valuation import value


def payoff_for(leg, mark, action, quote):
    spot = getattr(mark, leg.underlying.lower())
    payoff = intrinsic(leg, spot)
    action = expiry_action(leg, action, payoff)
    if action == "close":
        payoff = quote if quote is not None else value(leg, mark)
    elif action == "expire":
        payoff = Decimal(0)
    if action == "exercise" and leg.settlement == "physical":
        payoff = exercise_value(leg, spot)
    return action, payoff


def exercise_value(leg, spot):
    return spot - leg.strike if leg.kind == "call" else leg.strike - spot


def expiry_action(leg, action, payoff):
    if action == "expire" and payoff and leg.expiry_rule == "exercise_if_itm":
        return "exercise"
    return action
