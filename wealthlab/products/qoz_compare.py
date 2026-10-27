"""Identical contract economics under conditional tax treatments; separate liquid reference."""

from wealthlab.household.projection import project
from wealthlab.products.long_short_book import ZERO
from wealthlab.products.qoz_authorities import CHECKED, SOURCES


def compare(scenario):
    if scenario.qoz_plan is None:
        raise ValueError("A QOZ contract is required.")
    plan = scenario.qoz_plan
    policies = {
        name: plan.model_copy(update=dict(federal=name, mode="fund"))
        for name in ("denied", "deferred", "allowed")
    }
    policies["timely_exit"] = policies["allowed"].model_copy(
        update=dict(sale_not_before=plan.sale_requested, settlement_months=0)
    )
    # NJ may independently limit benefits; no unsupported NJ-only federal election is granted.
    policies["liquid_reference"] = plan.model_copy(
        update=dict(
            mode="liquid_reference", federal="denied", new_jersey="denied", settlement_months=0
        )
    )
    rows = {
        name: project(scenario.model_copy(update=dict(qoz_plan=policy)))
        for name, policy in policies.items()
    }
    return dict(
        input=scenario.model_dump(mode="json"),
        source_checked=CHECKED,
        authorities=SOURCES,
        rows=rows,
        outcomes={name: outcome(items) for name, items in rows.items()},
    )


def outcome(rows):
    final = rows[-1]
    return dict(
        net_wealth=final["net_wealth"],
        closing_cash=final["closing_cash"],
        restricted_nav=final["qoz_nav"] - final["qoz_receivable"],
        settlement_receivable=final["qoz_receivable"],
        funding_failure_months=sum(bool(r["funding_failure"]) for r in rows),
        tax_unfunded=sum((r.get("tax_unfunded", ZERO) for r in rows), ZERO),
        calls_unfunded=sum((r["qoz_call_unfunded"] for r in rows), ZERO),
    )
