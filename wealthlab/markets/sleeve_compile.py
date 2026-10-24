"""Bind complete monthly sleeve observations to the same realized household path."""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.markets.wrapper_compile import event_id


def validate(scenario, batch, binding):
    selected = binding.sleeves
    sleeves = (
        {s.account_id: s for s in scenario.sleeve_plan.sleeves} if scenario.sleeve_plan else {}
    )
    if len(selected) != len(set(selected)) or not set(selected) <= sleeves.keys():
        raise ValueError("Bind each known household sleeve account once.")
    if selected and not binding.replace_sleeve_observations_confirmed:
        raise ValueError("Confirm replacement of entered household sleeve observations.")
    for identity in selected:
        validate_factors(sleeves[identity].case, batch.assets)


def validate_factors(case, assets):
    if {case.long_factor, case.short_factor} - set(assets):
        raise ValueError("Unknown market factor in household sleeve.")


def compile_plans(payload, scenario, batch, binding, index):
    for sleeve in payload["sleeve_plan"]["sleeves"] if payload.get("sleeve_plan") else []:
        if sleeve["account_id"] not in binding.sleeves:
            continue
        case = sleeve["case"]
        long, short = (
            batch.assets.index(case["long_factor"]),
            batch.assets.index(case["short_factor"]),
        )
        sleeve["observations"] = [
            observation(sleeve["account_id"], start, end, batch, index, month, long, short, case)
            for month, (start, end) in enumerate(months(scenario.start, scenario.end))
        ]


def observation(identity, start, end, batch, index, month, long, short, case):
    return dict(
        id=event_id(identity, start, "sleeve_observation"),
        provenance="assumption",
        date=end - timedelta(days=1),
        long_return=rate(batch.mark_returns[index, month, long]),
        short_return=rate(batch.mark_returns[index, month, short]),
        long_yield=rate(batch.cash_yields[index, month, long]),
        short_yield=rate(batch.cash_yields[index, month, short]),
        locked=bool(
            (Decimal(case["long_multiple"]) and batch.locked[month, long])
            or (Decimal(case["short_multiple"]) and batch.locked[month, short])
        ),
    )


def rate(value):
    return Decimal(str(value)).quantize(Decimal(".000000000001"))
