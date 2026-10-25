"""Policy reserves use actual dated obligations, never twelve times a lump annual premium."""

from datetime import timedelta
from decimal import Decimal
from math import ceil

from wealthlab.household.calendar import months
from wealthlab.products.life_contract_tax import TERMINAL
from wealthlab.products.life_illustration_flows import OUTFLOWS

ZERO = Decimal(0)


def reserve_end(when, years):
    return when + timedelta(days=ceil(365.25 * years))


def required_values(scenario, contract):
    terminal = [e.date for e in contract.events if e.kind in TERMINAL]
    closed = terminal[0] if terminal else scenario.end
    return {
        end - timedelta(days=1)
        for _, end in months(scenario.start, scenario.end)
        if end - timedelta(days=1) < closed
    }


def reserve(holding, when, years, closed):
    if closed:
        return ZERO
    until = reserve_end(when, years)
    return sum(
        (
            e.amount
            for e in holding.contract.events
            if when <= e.date < until and e.kind in OUTFLOWS
        ),
        ZERO,
    )
