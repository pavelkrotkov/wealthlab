"""Require native economic closure and all supplied product tax recognition.

These checks consume executed books, never input exit requests. Product
contracts and tax schedules stay common across candidates; this layer does not
invent a tax schedule or illustration for a different allocation or premium.
"""

from decimal import Decimal

from wealthlab.optimization.account_exits import lots_closed
from wealthlab.optimization.contract_exits import employer_closed, options_closed
from wealthlab.optimization.drilling_exits import completed as drilling_closed
from wealthlab.optimization.qoz_exits import completed as qoz_closed


def complete(household, row):
    return (
        sleeves_closed(household, row)
        and exchange_closed(household, row)
        and life_closed(household, row)
        and options_closed(household, row)
        and employer_closed(household, row)
        and drilling_closed(household, row)
        and qoz_closed(household, row)
        and property_closed(household, row)
    )


def zero(state, names):
    return all(name in state and Decimal(state[name]) == 0 for name in names)


def sleeves_closed(household, row):
    if household.sleeve_plan is None:
        return True
    latest = {r["account_id"]: r for r in row.get("sleeve_audit", [])}
    return all(
        sleeve_closed(latest.get(s.account_id, {}).get("exit_state"))
        for s in household.sleeve_plan.sleeves
    )


def sleeve_closed(state):
    if state is None or state["unrecognized_future_events"]:
        return False
    if state["kind"] == "limited_liability_fund":
        return (
            state["investor_interest_closed"]
            and state["limited_liability_no_calls_assumed"]
            and not state["settlements"]
            and zero(state["outside_basis"], ("federal", "new_jersey"))
        )
    return state["closed"] and zero(
        state,
        ("long_value", "short_liability", "short_collateral", "free_cash", "financing_loan"),
    )


def exchange_closed(household, row):
    if household.exchange_fund_plan is None:
        return True
    audit = row.get("exchange_fund_audit", {})
    state = audit.get("terminal_state")
    if state is None:
        return False
    return (
        not state["active"]
        and zero(state, ("nav", "cash", "opening_cash_due", "fees_due"))
        and lots_closed(audit["remaining_lots"])
        and not audit["unrecognized_future_events"]
    )


def life_closed(household, row):
    if household.life_plan is None:
        return True
    values = {p["account_id"]: p for p in row.get("life_policy_values", [])}
    return all(
        policy_closed(values.get(holding.account_id)) for holding in household.life_plan.holdings
    )


def policy_closed(value):
    return (
        value is not None
        and value["closed"]
        and zero(value, ("loan", "net_cash_value", "net_surrender_value", "net_death_benefit"))
    )


def property_closed(household, row):
    if household.property_plan is None:
        return True
    states = {p["account_id"]: p for p in row.get("property_audit", {}).get("economic_state", [])}
    return all(
        h.account_id in states
        and states[h.account_id]["closed"]
        and not states[h.account_id]["blocked"]
        and zero(states[h.account_id], ("gross_value", "linked_debt_balance"))
        for h in household.property_plan.holdings
    )
