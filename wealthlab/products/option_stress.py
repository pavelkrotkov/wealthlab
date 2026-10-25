"""Independent stock/index shocks value every leg; protection is never extrapolated."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.option_math import direction, units
from wealthlab.products.option_valuation import value


def stress(case, *, stock_shocks=(-0.4, 0, 0.4), index_shocks=(-0.4, 0, 0.4)):
    mark = case.marks[0]
    quantity = sum((lot.quantity for lot in case.holdings.lots), Decimal(0))
    opening = [leg for leg in case.legs if leg.opened == mark.date]
    cash, fees = opening_cash(case, opening)
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
                    index_shock=index,
                    stock_value=money(quantity * shocked.stock),
                    option_value=sum(leg_values.values(), Decimal(0)),
                    wealth=cash + quantity * shocked.stock + sum(leg_values.values(), Decimal(0)),
                    unwind_cost=fees + case.stock_sale_fee,
                    legs=leg_values,
                )
            )
    return rows


def opening_cash(case, legs):
    cash = case.holdings.accounts[0].cash + case.outside_cash
    cash -= sum(direction(leg) * units(leg) * leg.premium + leg.opening_fee for leg in legs)
    return cash, sum(leg.closing_fee for leg in legs)
