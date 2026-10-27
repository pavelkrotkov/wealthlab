"""Reuse the native price-only exchange adapter on a subset of the shared market path.

The security-to-factor map permits a common equity factor without renaming
other household securities. Cash distributions and their tax allocations stay
independently supplied: a positive factor cash yield cannot silently disappear.
"""

from dataclasses import replace

from wealthlab.products.exchange_fund_market import bind


def validate(scenario, batch, binding):
    factors = binding.exchange_factors
    if not factors:
        return
    plan = scenario.exchange_fund_plan
    if plan is None or set(factors) != set(plan.opening_prices):
        raise ValueError("Bind every known exchange source and basket security exactly once.")
    if not binding.replace_exchange_observations_confirmed:
        raise ValueError("Confirm replacement of supplied exchange price observations.")
    if set(factors.values()) - set(batch.assets):
        raise ValueError("Unknown market factor in exchange-fund binding.")


def compile_plan(payload, scenario, batch, binding, index):
    if not binding.exchange_factors:
        return
    factors = binding.exchange_factors
    indices = [batch.assets.index(factor) for factor in factors.values()]
    selected = replace(
        batch,
        assets=tuple(factors),
        mark_returns=batch.mark_returns[:, :, indices],
        cash_yields=batch.cash_yields[:, :, indices],
        locked=batch.locked[:, indices],
    )
    result = bind(scenario, selected, index)
    payload["exchange_fund_plan"] = result.exchange_fund_plan.model_dump(mode="json")
