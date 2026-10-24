"""Funding outcomes concern the supplied horizon, not an inferred retirement guarantee."""

from calendar import monthrange
from datetime import date
from decimal import Decimal
from math import sqrt
from statistics import NormalDist

from wealthlab.household.funding import opening_wealth
from wealthlab.tax.payments import missed_schedule


def summarize(scenario, rows, index):
    return dict(
        **funding(rows),
        path=index,
        net_wealth_drawdown=drawdown(scenario, rows),
        max_security_weight=max(r["market_max_security_weight"] for r in rows),
        ending_nominal_wealth=rows[-1]["net_wealth"],
        ending_real_wealth=rows[-1]["real_net_wealth"],
        terminal_tax_position=rows[-1].get("tax_position", Decimal(0)),
    )


def aggregate(scenario, batch, results):
    successes = sum(r["funded"] for r in results)
    fraction = successes / len(results)
    stochastic = batch.metadata["input"]["mode"] == "monte_carlo"
    youngest = max(m.birth_date for m in scenario.members)
    year = youngest.year + scenario.target_age + 1
    target = date(year, youngest.month, min(youngest.day, monthrange(year, youngest.month)[1]))
    attained = scenario.end >= target
    return dict(
        paths=len(results),
        successes=successes,
        funding_fraction=fraction,
        monte_carlo_95_wilson=wilson(successes, len(results)) if stochastic else None,
        target_success=scenario.target_success,
        target_point_estimate_met=fraction >= scenario.target_success,
        horizon_covers_target_age=attained,
        target_age=scenario.target_age,
        end=scenario.end.isoformat(),
        scope="Supplied-horizon funding under entered policy and tax assumptions",
    )


def wilson(successes, count):
    # NIST/SEMATECH section 7.2.4.1: two-sided Wilson score, no continuity adjustment.
    z = NormalDist().inv_cdf(0.975)
    p = successes / count
    denominator = 1 + z * z / count
    center = (p + z * z / (2 * count)) / denominator
    radius = z * sqrt(p * (1 - p) / count + z * z / (4 * count * count)) / denominator
    return [max(0, center - radius), min(1, center + radius)]


def drawdown(scenario, rows):
    peak = opening_wealth(scenario)
    result = Decimal(0)
    for row in rows:
        peak = max(peak, row["net_wealth"])
        if peak > 0:
            result = max(result, (peak - row["net_wealth"]) / peak)
    return result


def funding(rows):
    failures = [r for r in rows if r["funding_failure"]]
    return dict(
        funded=not failures,
        discretionary_spending_reduction=sum(
            (r.get("guardrail_discretionary_reduction", 0) for r in rows), Decimal(0)
        ),
        first_failure=failures[0]["date"] if failures else None,
        funding_shortfall=sum((r["funding_shortfall"] for r in rows), Decimal(0)),
        missed_tax_schedule_months=sum(missed_schedule(r) for r in rows),
        cash_reserve_breach_months=sum(r["closing_cash"] < r["reserve_target"] for r in rows),
    )
