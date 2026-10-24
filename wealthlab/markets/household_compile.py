"""Compile realized month-end marks without using future returns to choose trades."""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.household.scenario import Scenario
from wealthlab.markets.employer_compile import compile_plans as compile_employers
from wealthlab.markets.medical_inflation import compile_bills
from wealthlab.markets.sleeve_compile import compile_plans as compile_sleeves
from wealthlab.markets.wrapper_compile import compile_plans


def compile_marks(scenario, batch, binding, index):
    payload = scenario.model_dump(mode="json")
    compile_plans(payload, scenario, batch, binding, index)
    compile_employers(payload, scenario, batch, binding, index)
    compile_sleeves(payload, scenario, batch, binding, index)
    compile_bills(payload, scenario, batch, binding, index)
    if scenario.lot_plan is not None:
        compile_lots(payload, scenario, batch, binding, index)
    return Scenario.model_validate(payload)


def compile_lots(payload, scenario, batch, binding, index):
    linked = payload["lot_plan"]
    prices = dict(scenario.lot_plan.opening_prices)
    factors = {b.security_id: batch.assets.index(b.factor) for b in binding.securities}
    snapshots = []
    for month, (_, end) in enumerate(months(scenario.start, scenario.end)):
        prices = {
            security: (
                price * Decimal(str(1 + batch.mark_returns[index, month, factors[security]]))
            ).quantize(Decimal(".00000001"))
            for security, price in prices.items()
        }
        if any(p <= 0 for p in prices.values()):
            raise ValueError("Zero-price/delisted securities need a terminal write-off adapter.")
        snapshots.append(dict(date=end - timedelta(days=1), prices=dict(prices)))
    linked["monthly_marks"] = snapshots
    linked["case"]["closing_prices"] = prices
