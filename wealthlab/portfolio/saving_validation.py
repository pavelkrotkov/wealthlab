"""Saving budgets are observed month-end choices, not future market information."""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import months


def validate(plan, scenario):
    policies = plan.savings
    validate_ids(plan, policies)
    accounts = {a.id for a in plan.case.accounts}
    securities = {s.id for s in plan.case.securities}
    dates = {end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)}
    for policy in policies:
        validate_policy(policy, accounts, securities, dates)


def validate_policy(policy, accounts, securities, dates):
    if policy.account_id not in accounts or set(policy.target_weights) - securities:
        raise ValueError("Saving allocations require known linked taxable accounts and securities.")
    if policy.date not in dates:
        raise ValueError("Saving allocations require an observed household month-end date.")
    if sum(policy.target_weights.values(), Decimal(0)) != 1:
        raise ValueError("Saving target weights must sum to one.")
    if policy.provenance == "unresolved":
        raise ValueError("Resolve the saving allocation before projecting it.")


def validate_ids(plan, policies):
    identities = [p.id for p in policies]
    reserved = {p.id for p in plan.rebalances} | {t.id for t in plan.case.trades}
    if len(identities) != len(set(identities)) or set(identities) & reserved:
        raise ValueError("Saving policy IDs must be unique and separate from other orders.")
