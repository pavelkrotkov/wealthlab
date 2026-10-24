"""Explicit month-end employee-plan returns follow actual funded payroll elections.

The household payroll book is monthly. Earlier return events cannot be priced
honestly against its pooled wage-funded deposits, so manual schedules require
month ends. This layer never makes plan assets available for household sales.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import money, months
from wealthlab.retirement.account_liquidity import validate as validate_locks


def validate(scenario):
    plan = scenario.workplace_plan
    validate_locks(plan.liquidity_locks, set(plan.products), scenario.start, scenario.end)
    records = [*plan.orders, *plan.returns, *plan.liquidity_locks]
    identities = [r.id for r in records]
    if len(identities) != len(set(identities)):
        raise ValueError("Employee election/return/lock IDs must be unique.")
    if any(r.provenance == "unresolved" for r in plan.returns):
        raise ValueError("Resolve workplace return assumptions before projecting.")
    ends = {end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)}
    for event in plan.returns:
        validate_event(event, plan.products, ends)


def apply(plan, wallet, start, end, audit):
    total = Decimal(0)
    for event in sorted(plan.returns, key=lambda e: e.date):
        if start <= event.date < end:
            before = wallet.balances[event.account_id]
            change = money(before * event.rate)
            wallet.balances[event.account_id] += change
            total += change
            audit.append(
                dict(
                    id=event.id,
                    date=event.date,
                    account_id=event.account_id,
                    opening=before,
                    market_change=change,
                    closing=wallet.balances[event.account_id],
                )
            )
    return total


def validate_event(event, products, month_ends):
    if event.account_id not in products or event.date not in month_ends:
        raise ValueError("Employee-plan returns require known workplace accounts and month ends.")
