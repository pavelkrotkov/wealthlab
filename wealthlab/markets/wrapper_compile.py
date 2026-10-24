"""Reuse dated return/lock inputs without supplying future cash to earlier orders.

Each supported account is explicitly assumed to be a single return-factor
proxy. Cash yield stays inside it. The full monthly mark change plus cash yield
applies to the balance immediately before the month-end return event, without
a multiplicative cross term or daily interpolation. Earlier withdrawals do
not receive that later return; deposits present at month end receive it.
Original source schedules remain in the run export; only a compiled copy changes.
"""

from datetime import timedelta
from decimal import Decimal
from hashlib import sha256

from wealthlab.household.calendar import months


def compile_plans(payload, scenario, batch, binding, index):
    for wrapper in binding.wrappers:
        kind = plan_kind(scenario, wrapper.account_id)
        plan = payload[kind]
        identity = wrapper.account_id
        plan["returns"] = [r for r in plan["returns"] if r["account_id"] != identity]
        factor = batch.assets.index(wrapper.factor)
        for month, (start, end) in enumerate(months(scenario.start, scenario.end)):
            rate = Decimal(str(batch.mark_returns[index, month, factor]))
            rate += Decimal(str(batch.cash_yields[index, month, factor]))
            plan["returns"].append(
                dict(
                    id=event_id(identity, start, "return"),
                    provenance="assumption",
                    date=end - timedelta(days=1),
                    account_id=identity,
                    rate=rate.quantize(Decimal(".000000000001")),
                )
            )
            if batch.locked[month, factor]:
                plan["liquidity_locks"].append(
                    dict(
                        id=event_id(identity, start, "lock"),
                        provenance="assumption",
                        account_id=identity,
                        start=start,
                        end=end,
                    )
                )


def plan_kind(scenario, identity):
    if scenario.ira_plan and identity in scenario.ira_plan.products:
        return "ira_plan"
    if scenario.education_plan and identity in {
        a.account_id for a in scenario.education_plan.accounts
    }:
        return "education_plan"
    raise ValueError(
        "Market wrapper bindings require a supported ordinary IRA or household 529 plan."
    )


def event_id(identity, when, kind):
    digest = sha256(f"{identity}:{when}:{kind}".encode()).hexdigest()[:40]
    return f"market_{kind}_{digest}"


def validate(scenario, batch, binding):
    identities = [w.account_id for w in binding.wrappers]
    if len(identities) != len(set(identities)):
        raise ValueError("Bind each wrapper account once.")
    accounts = {a.id for a in scenario.accounts}
    for wrapper in binding.wrappers:
        if wrapper.account_id not in accounts or wrapper.factor not in batch.assets:
            raise ValueError("Unknown account or factor in wrapper market binding.")
        if not wrapper.replace_entered_returns_confirmed:
            raise ValueError("Confirm replacement of the bound account's entered return schedule.")
        plan_kind(scenario, wrapper.account_id)
