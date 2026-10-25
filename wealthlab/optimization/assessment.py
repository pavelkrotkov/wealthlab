"""Rank only completed exits; recognized-tax marks are not spendable terminal wealth."""

from decimal import Decimal
from math import ceil
from statistics import median

from wealthlab.markets.household_report import wilson
from wealthlab.optimization.metrics import financial_metrics


def assess(case, household, result, sampled=True):
    outcomes = result["outcomes"]
    count = len(outcomes)
    funded = sum(r["joint_feasible"] for r in outcomes)
    reserved = sum(r["cash_reserve_breach_months"] == 0 for r in outcomes)
    exits = exit_status(household, result)
    wealth = [r["ending_real_wealth"] for r in outcomes]
    checks = constraints(case, result, exits, funded / count, reserved / count)
    return dict(
        eligible=all(checks.values()),
        constraints=checks,
        unmet_constraints=[key for key, passed in checks.items() if not passed],
        paths=count,
        joint_success_fraction=funded / count,
        joint_success_95_wilson=interval(funded, count, sampled),
        reserve_success_fraction=reserved / count,
        reserve_success_95_wilson=interval(reserved, count, sampled),
        median_real_after_tax_exit_wealth=median(wealth) if all(exits) else None,
        downside_real_after_tax_exit_wealth=sorted(wealth)[ceil(0.05 * count) - 1]
        if all(exits)
        else None,
        median_marked_real_wealth=median(wealth),
        **financial_metrics(result),
    )


def completed_exit(household, rows):
    # Supplied/native exits must actually execute. An exit request or high marked
    # value cannot stand in for disposal, loan satisfaction or recognized tax.
    cash = {a.id for a in household.accounts if a.wrapper == "cash"}
    balances = rows[-1]["account_balances"]
    lots = rows[-1].get("lot_audit", {}).get("lots", [])
    return all(value == 0 for key, value in balances.items() if key not in cash) and all(
        Decimal(lot["quantity"]) == 0 for lot in lots
    )


def constraints(case, result, exits, funded, reserved):
    outcomes = result["outcomes"]
    return dict(
        target_age_horizon=result["aggregate"]["horizon_covers_target_age"],
        spending_and_product_safety=funded >= case.targets.success_fraction,
        cash_reserve=reserved >= case.targets.success_fraction,
        completed_after_tax_exit=all(exits),
        complete_tax_years=not any(r["partial_tax_years"] for r in outcomes),
        resolved_tax_years=not any(r["provisional_tax_years"] for r in outcomes),
        issuer_limit=concentration(case.targets.maximum_issuer_weight, outcomes),
    )


def concentration(limit, outcomes):
    if limit is None:
        return True
    return all(
        r["issuer_concentration_complete"]
        and r["max_security_weight"] is not None
        and r["max_security_weight"] <= limit
        for r in outcomes
    )


def score(assessment):
    return (
        assessment["joint_success_fraction"],
        assessment["median_real_after_tax_exit_wealth"] or Decimal(0),
    )


def exit_status(household, result):
    return [completed_exit(household, item["rows"]) for item in result["details"]]


def interval(successes, count, sampled):
    return wilson(successes, count) if sampled else None
