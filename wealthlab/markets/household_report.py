"""Funding outcomes concern the supplied horizon, not an inferred retirement guarantee."""

from calendar import monthrange
from datetime import date
from decimal import Decimal
from math import sqrt
from statistics import NormalDist

from wealthlab.household.funding import opening_wealth
from wealthlab.markets.household_outcomes import funding, product_totals
from wealthlab.markets.hsa_payroll_report import summary as hsa_summary
from wealthlab.portfolio.rebalance_state import summary as rebalance_summary
from wealthlab.tax.household_reporting import summary as tax_summary


def summarize(scenario, rows, index):
    return dict(
        **funding(rows),
        **tax_summary(rows),
        **hsa_summary(scenario, rows),
        **rebalance_summary(rows),
        path=index,
        net_wealth_drawdown=drawdown(scenario, rows),
        max_security_weight=known_weight(rows),
        issuer_concentration_complete=all(r["market_issuer_concentration_complete"] for r in rows),
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
        **product_totals(results),
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


def known_weight(rows):
    known = [
        r["market_max_security_weight"] for r in rows if r["market_max_security_weight"] is not None
    ]
    return max(known) if known else None
