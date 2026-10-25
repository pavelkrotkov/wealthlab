"""Reject ambiguous transfer identity and unsupported sources before any household cash moves."""

from wealthlab.retirement.ira_household_deposit_validation import PREFIX as FUNDING_PREFIX
from wealthlab.retirement.workplace_rmd_validation import PREFIX as RMD_PREFIX
from wealthlab.retirement.workplace_withdrawal_validation import validate_order


def orders(scenario):
    workplace = scenario.workplace_plan
    cash = workplace.cash_withdrawals if workplace is not None else None
    return cash.direct_rollovers if cash is not None else []


def validate(scenario):
    transfers = orders(scenario)
    if not transfers:
        return
    ira = scenario.ira_plan
    if ira is None:
        raise ValueError("Direct plan rollovers require the household ordinary IRA ledger.")
    cash = scenario.workplace_plan.cash_withdrawals
    accounts = {a.id: a for a in scenario.accounts}
    validate_ids(scenario, transfers)
    for order in transfers:
        validate_order(order, cash.profiles, scenario)
        if ira.products.get(order.destination) != "traditional_ira":
            raise ValueError("Direct plan cash requires a known ordinary traditional IRA target.")
        if accounts[order.source].owner != accounts[order.destination].owner:
            raise ValueError("Direct plan rollovers must preserve the source account owner.")


def validate_ids(scenario, transfers):
    ira = scenario.ira_plan
    workplace = scenario.workplace_plan
    records = [
        *transfers,
        *workplace.cash_withdrawals.orders,
        *workplace.orders,
        *workplace.returns,
        *workplace.liquidity_locks,
        *ira.owners,
        *ira.orders,
        *ira.returns,
        *ira.liquidity_locks,
        *scenario.accounts,
    ]
    if ira.contributions is not None:
        records.extend(ira.contributions.orders)
    ids = [r.id for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Plan rollovers and their IRA/workplace records need unique IDs.")
    if any(o.id.startswith((FUNDING_PREFIX, RMD_PREFIX)) for o in transfers):
        raise ValueError("Direct plan rollover IDs cannot use reserved internal prefixes.")
