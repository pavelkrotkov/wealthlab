"""Sell overweights, then allocate only new sale proceeds to underweight holdings.

The drift band triggers a complete dated decision. The sale cap limits gross
shares sold as a fraction of starting marked securities, not round-trip turnover.
Underfunded buys are proportional to target-dollar gaps after reserving each
commission. Stable security ordering and down-rounded shares leave honest drift.
"""

from wealthlab.portfolio.rebalance_orders import buy, sell
from wealthlab.portfolio.rebalance_state import ZERO, report, snapshot, values


def execute(lots, start, end):
    for policy in lots.plan.rebalances:
        if start <= policy.date < end:
            lots.rebalance_decisions.append(decide(lots.book, policy, lots.prices, lots.locked))


def decide(book, policy, prices, locked):
    state = snapshot(book, policy, prices)
    drift = max(
        abs(state["weights"][key] - weight) for key, weight in policy.target_weights.items()
    )
    status = "no marked securities"
    if state["total"] > 0:
        status = "within drift band"
        if drift > policy.drift_band:
            sales(book, policy, prices, state, locked)
            purchases(book, policy, prices, state, locked)
            status = "executed" if len(book.history) > state["history"] else "constrained"
    return report(book, policy, prices, state, status, locked)


def sales(book, policy, prices, state, locked):
    remaining = state["total"] * policy.max_sale_fraction
    for key in sorted(state["before"]):
        excess = max(ZERO, state["before"][key] - state["targets"][key])
        if excess and key not in locked:
            remaining -= sell(book, policy, key, prices[key], min(excess, remaining))


def purchases(book, policy, prices, state, locked):
    holdings = values(book, policy, prices)
    gaps = {
        key: state["targets"][key] - value
        for key, value in holdings.items()
        if value < state["targets"][key] and key not in locked
    }
    cash = book.cash[policy.account_id] - state["cash"]
    budget = cash - len(gaps) * policy.commission_per_trade
    total = sum(gaps.values(), ZERO)
    if budget <= 0 or total <= 0:
        return
    for key in sorted(gaps):
        buy(book, policy, key, prices[key], min(budget, total) * gaps[key] / total)
