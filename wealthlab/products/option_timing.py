"""Ex-date entitlement precedes delivery; rolls close existing legs before new premiums."""

from wealthlab.products.option_events import finish
from wealthlab.products.option_stock import shares


def dividends(state, mark):
    for index, item in enumerate(state.case.dividends):
        if item.ex_date == mark.date:
            state.entitlements[index] = shares(state) * item.per_share
        if item.pay_date == mark.date:
            state.cash(state.entitlements.pop(index), "stock_dividend", mark.date)


def terminations(state, mark, *, same_day):
    events = {event.leg_id: event for event in state.case.events}
    for leg in list(state.active.values()):
        if (leg.opened == mark.date) != same_day:
            continue
        event = events.get(leg.id)
        if event and event.date == mark.date:
            finish(state, leg, mark, event.action, event.close_price)
        elif leg.expiry == mark.date:
            finish(state, leg, mark, "expire")
