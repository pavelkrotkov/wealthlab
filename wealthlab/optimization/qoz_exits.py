"""Executed shareholder closure differs from zero NAV or discharge of entity creditors.

A supplied limited-liability corporation may retain internal insolvency debt
without household recourse. Its actual stock sale, settlement and recognized
basis must still close; a marked-zero but unsold interest is not an exit.
"""

from wealthlab.optimization.drilling_state import zero
from wealthlab.optimization.qoz_exit_state import shareholder_closed


def completed(household, row):
    if not isinstance(row, dict):
        return False
    plan = household.qoz_plan
    audit = row.get("qoz_audit")
    if plan is None:
        return audit is None
    audit = valid_audit(row, plan)
    if audit is None:
        return False
    state = audit["economic_state"]
    if state is None:
        return unfunded(plan, audit)
    return shareholder_closed(state, audit, plan)


def unfunded(plan, audit):
    return (
        calls_unfunded(plan, audit.get("calls"))
        and audit.get("tranches") == []
        and audit.get("ending_entity") is None
    )


def calls_unfunded(plan, calls):
    if not isinstance(calls, list) or len(calls) != len(plan.calls):
        return False
    if not all(unfunded_call(call) for call in calls):
        return False
    return {call["call"]["id"] for call in calls} == {c.id for c in plan.calls}


def unfunded_call(call):
    return (
        isinstance(call, dict)
        and isinstance(call.get("call"), dict)
        and isinstance(call["call"].get("id"), str)
        and zero(call.get("funded"))
    )


def valid_audit(row, plan):
    audit, balances = row.get("qoz_audit"), row.get("account_balances")
    if not isinstance(audit, dict) or not isinstance(balances, dict):
        return None
    if "economic_state" not in audit or not zero(balances.get(plan.account_id)):
        return None
    return audit
