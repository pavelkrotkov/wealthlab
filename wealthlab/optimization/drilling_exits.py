"""Prove native book closure, never legal eligibility or complete household tax settlement.

The unused shadow reference book cannot block an actual property exit; likewise
reference closure must use its real share book, not the inactive property flags.
"""

from wealthlab.optimization.drilling_state import ending_state, zeros
from wealthlab.products.drilling_cash import COSTS


def completed(household, row):
    if not isinstance(row, dict):
        return False
    plan = household.drilling_plan
    audit = row.get("drilling_audit")
    if plan is None:
        return audit is None
    if plan.mode not in {"drilling", "liquid_reference"}:
        return False
    state = ending_state(plan, audit, row)
    if state is None:
        return False
    return actual_closed(state) if plan.mode == "drilling" else reference_closed(plan, state, audit)


def actual_closed(state):
    return (
        state.get("closed") is True
        and state.get("property_sold") is True
        and zeros(
            {key: state.get(key) for key in ("cash", "property_value")}, ("cash", "property_value")
        )
        and zeros(state.get("creditors"), (*COSTS, "exit_cost"))
        and zeros(state.get("basis"), ("federal", "nj", "at_risk"))
        and zeros(state.get("tangible_basis"), ("federal", "nj"))
    )


def reference_closed(plan, state, audit):
    return (
        audit.get("reference_lots") == []
        and state.get("reference_exit_pending") is False
        and zeros(state.get("reference_cash"), (plan.account_id,))
        and zeros(state.get("reference_pending_losses"), ("federal", "nj"))
    )
