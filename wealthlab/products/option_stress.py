"""Independent stock/index shocks value every leg; protection is never extrapolated."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.option_math import direction, units
from wealthlab.products.option_opening import opening_state
from wealthlab.products.option_stock import shares
from wealthlab.products.option_valuation import value


def stress(case, *, stock_shocks=(-0.4, 0, 0.4), index_shocks=(-0.4, 0, 0.4)):
    mark = case.marks[0]
    state, _row = opening_state(case)
    quantity = shares(state)
    opening = list(state.active.values())
    cash = state.book.cash[state.account] + state.reserve - state.loan
    fees = sum(leg.closing_fee for leg in opening)
    rows = []
    for stock in stock_shocks:
        for index in index_shocks:
            shocked = mark.model_copy(
                update=dict(
                    stock=mark.stock * (1 + Decimal(str(stock))),
                    index=mark.index * (1 + Decimal(str(index))),
                )
            )
            leg_values = {
                leg.id: money(direction(leg) * units(leg) * value(leg, shocked)) for leg in opening
            }
            rows.append(
                dict(
                    stock_shock=stock,
                    execution_failed=bool(state.failures),
                    opening_collateral_shortfall=_row["collateral_shortfall"],
                    index_shock=index,
                    stock_value=money(quantity * shocked.stock),
                    option_value=sum(leg_values.values(), Decimal(0)),
                    wealth=cash + quantity * shocked.stock + sum(leg_values.values(), Decimal(0)),
                    unwind_cost=fees + case.stock_sale_fee,
                    legs=leg_values,
                )
            )
    return rows
