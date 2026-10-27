"""Executed positions and separately supplied contractual rights must both be closed.

Zero net equity cannot close offsetting contracts, loans or an employer award.
A contract's legal termination creates no exemption from its supplied tax events.
"""


def options_closed(household, row):
    if household.option_plan is None:
        return True
    marks = row.get("option_mark_audit", [])
    state = marks[-1].get("exit_state") if marks else None
    if state is None or not state["modeled_cash_exit_complete"]:
        return False
    return not any(state[key] for key in ("cash", "outside_cash")) and tax_closed(
        row.get("option_tax_audit")
    )


def tax_closed(audit):
    return audit is not None and all(
        item["recognized"] is not None and not item["deferred"] and not item["unresolved"]
        for item in audit
    )


def employer_closed(household, row):
    if household.compensation_plan is None:
        return True
    observed = {
        item["tranche"]: item.get("exit_evidence") for item in row.get("employer_tranches", [])
    }
    return all(
        tranche_closed(observed.get(tranche.id)) for tranche in household.compensation_plan.tranches
    )


def tranche_closed(state):
    if state is None:
        return False
    return (
        state.get("contractual_exit_proven") is True
        and state["account_reconciles"]
        and state["dollar_positions_zero"]
        and state.get("future_supplied_tax_allocations_clear") is True
        and not state["declared_future_events"]
    )
