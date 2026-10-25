"""Compare actual household funding and protection on identical realized market paths.

Marked wealth subtracts recognized tax liabilities; unexecuted future exit taxes
remain outside that number. Death protection is never added to living wealth.
"""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.paths import generate
from wealthlab.products.life_comparison_validation import validate
from wealthlab.tax.household_reporting import summary as taxes

ZERO = Decimal(0)


def compare(case):
    validate(case)
    batch = generate(case.market) if case.market is not None else None
    results = {}
    for name, scenario in case.alternatives.items():
        if batch is None:
            details = [dict(path=0, rows=project(scenario))]
            market = None
        else:
            market = run(scenario, batch, case.binding)
            details = market["details"]
        results[name] = dict(
            details=details,
            market=market,
            outcomes=[outcome(item["rows"], item["path"]) for item in details],
        )
    return dict(
        inputs=case.model_dump(mode="json"),
        alternatives=results,
        reference=case.liquid_reference,
        batch=batch.export() if batch else None,
        differences=differences(results, case.liquid_reference, batch is not None),
    )


def outcome(rows, path):
    final = rows[-1]
    return dict(
        path=path,
        marked_wealth_after_recognized_tax=final["net_wealth"],
        closing_cash=final["closing_cash"],
        reserve_target=final["reserve_target"],
        reserve_breach_months=sum(r["closing_cash"] < r["reserve_target"] for r in rows),
        funding_failure_months=sum(bool(r["funding_failure"]) for r in rows),
        funding_shortfall=sum((r["funding_shortfall"] for r in rows), ZERO),
        ending_protection_gap=final["life_protection_shortfall"],
        maximum_protection_gap=max(r["life_protection_shortfall"] for r in rows),
        ending_death_protection=final["life_net_death_benefit"],
        premiums_from_retirement=sum((r["life_retirement_premiums_paid"] for r in rows), ZERO),
        future_retirement_premiums=final["life_future_retirement_premiums"],
        saving_spent=sum((r.get("saving_spent", ZERO) for r in rows), ZERO),
        saving_unfilled=sum((r.get("saving_unfilled", ZERO) for r in rows), ZERO),
        **taxes(rows),
    )


def differences(results, reference, market):
    baseline = results[reference]
    return {
        name: paired(baseline["market"], result["market"])
        if market
        else [
            dict(
                path=0,
                marked_wealth_change=result["outcomes"][0]["marked_wealth_after_recognized_tax"]
                - baseline["outcomes"][0]["marked_wealth_after_recognized_tax"],
            )
        ]
        for name, result in results.items()
        if name != reference
    }
