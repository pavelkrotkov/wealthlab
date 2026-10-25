"""Premium cash occurs once; physical exercise transfers its tax amount into the shares."""

from wealthlab.household.calendar import money
from wealthlab.products.option_math import direction, units
from wealthlab.products.option_payoff import payoff_for
from wealthlab.products.option_stock import trade_stock


def open_leg(state, leg, mark):
    amount = -direction(leg) * units(leg) * leg.premium - leg.opening_fee
    if amount < 0 and not state.fund(-amount):
        state.failures.append(f"{leg.id}: unfunded opening premium")
        return
    state.cash(amount, f"open:{leg.id}", mark.date)
    state.active[leg.id] = leg


def finish(state, leg, mark, action, quote=None):
    action, payoff = payoff_for(leg, mark, action, quote)
    fee = leg.expiry_fee if action == "expire" else leg.closing_fee
    physical = action == "exercise" and leg.settlement == "physical"
    if physical:
        if not trade_stock(state, leg, mark):
            return
    else:
        state.cash(
            money(direction(leg) * units(leg) * payoff) - fee,
            f"{action}:{leg.id}",
            mark.date,
        )
    pnl = money(direction(leg) * units(leg) * (payoff - leg.premium)) - leg.opening_fee - fee
    row = dict(
        id=f"{leg.id}:{mark.date}",
        leg_id=leg.id,
        date=mark.date.isoformat(),
        action=action,
        physical=physical,
        pnl=pnl,
        payoff=payoff,
        termination_fee=fee,
        federal_class=leg.federal_class,
        federal_character=leg.federal_character,
    )
    state.closed[leg.id] = row
    state.recognition.append(row)
    del state.active[leg.id]
