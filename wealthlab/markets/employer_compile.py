"""Compile only prefix-observed employer returns into existing dated tranche events.

Net marks apply at month end to remaining vested/contingent values. Existing
allocations, grants, vesting and elections stay supplied, with explicit sequence
numbers; generated collisions fail existing validation instead of reordering.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.markets.employment_compile import compile_link
from wealthlab.markets.wrapper_compile import event_id


def compile_plans(payload, scenario, batch, binding, index):
    for item in binding.employers:
        compile_account(payload, scenario, batch, item, index)


def compile_account(payload, scenario, batch, item, index):
    tranches = [t for t in scenario.compensation_plan.tranches if t.account == item.account_id]
    ids = {t.id for t in tranches}
    plan = payload["compensation_plan"]
    replace_returns(plan, ids)
    factor = batch.assets.index(item.factor)
    for month, (start, end) in enumerate(months(scenario.start, scenario.end)):
        append_returns(plan, item, tranches, start, end, batch.mark_returns[index, month, factor])
        if batch.locked[month, factor]:
            plan["liquidity_locks"].append(
                dict(
                    id=event_id(item.account_id, start, "employer_lock"),
                    provenance="assumption",
                    account_id=item.account_id,
                    start=start,
                    end=end,
                )
            )
    if item.employment:
        compile_link(payload, scenario, batch, item, index, tranches)


def append_returns(plan, item, tranches, start, end, rate):
    for offset, tranche in enumerate(tranches):
        plan["events"].append(
            dict(
                id=event_id(tranche.id, start, "employer_return"),
                provenance="assumption",
                date=end - timedelta(days=1),
                sequence=item.event_sequence_start + offset,
                tranche=tranche.id,
                kind="net_return",
                rate=Decimal(str(rate)).quantize(Decimal(".000000000001")),
            )
        )


def replace_returns(plan, tranche_ids):
    plan["events"] = [
        e for e in plan["events"] if e["kind"] != "net_return" or e["tranche"] not in tranche_ids
    ]
