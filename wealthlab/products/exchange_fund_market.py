"""Bind one already-realized, price-only path to both policies without resampling."""

from decimal import Decimal

import numpy as np

from wealthlab.household.calendar import months


def bind(scenario, batch, path=0):
    plan = scenario.exchange_fund_plan
    dates = tuple(start for start, _ in months(scenario.start, scenario.end))
    if tuple(batch.dates) != dates or not 0 <= path < len(batch.mark_returns):
        raise ValueError("Exchange market path must cover the household horizon and selected path.")
    if set(batch.assets) != set(plan.opening_prices):
        raise ValueError("Exchange market factors must match all source and basket securities.")
    if np.any(batch.cash_yields):
        raise ValueError(
            "Exchange path binding needs zero cash yields; distributions are separate."
        )
    if not np.isfinite(batch.mark_returns).all() or np.any(batch.mark_returns <= -1):
        raise ValueError("Exchange marks must be finite and above complete write-off.")
    return apply(scenario, batch, path)


def apply(scenario, batch, path):
    plan = scenario.exchange_fund_plan
    prices = dict(plan.opening_prices)
    observations = []
    for i, observation in enumerate(plan.observations):
        for j, identity in enumerate(batch.assets):
            prices[identity] = prices[identity] * Decimal(str(1 + batch.mark_returns[path, i, j]))
            prices[identity] = prices[identity].quantize(Decimal(".00000001"))
        observations.append(
            observation.model_copy(
                update={"prices": dict(prices), "locked": bool(batch.locked[i].any())}
            )
        )
    return scenario.model_copy(
        update={"exchange_fund_plan": plan.model_copy(update={"observations": observations})}
    )
