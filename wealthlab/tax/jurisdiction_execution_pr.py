"""Bind the native PR assessment to actual paid-US-tax positions in the shared book.

A complete full-year source profile supplies the local facts. The consumer
recalculates the native ordinary assessment after actual federal credit and
payment execution. It neither subtracts an extra US credit nor moves cash.
"""

from datetime import date

from wealthlab.tax.pr_execution_context import prepare
from wealthlab.tax.pr_execution_paid_tax import evaluate as actual
from wealthlab.tax.pr_inputs import income
from wealthlab.tax.pr_local import calculate
from wealthlab.tax.pr_recognition import recognized


def assessments(scenario, observed=None):
    results, amounts = {}, {}
    for annual in scenario.tax_plan.cases:
        if annual.pr_federal is None:
            continue
        year = annual.policy.year
        target = binding(scenario, year)
        result = native_result(annual, observed)
        results[target.id] = result
        amounts[target.id] = result["assessment"]["income_tax"]
    return amounts, results


def complete_annual(annual):
    profile = annual.pr_federal.model_copy(update=dict(as_of=date(annual.policy.year, 12, 31)))
    rows = [r.income for r in profile.sources]
    full = annual.model_copy(update=dict(pr_federal=profile, federal_income=income(rows)))
    return full


def binding(scenario, year):
    candidates = [
        a
        for a in scenario.foreign_tax_plan.assessments
        if (a.country, a.liability_year, a.tax_type) == ("PR", year, "income")
    ]
    if len(candidates) != 1:
        raise ValueError(
            "Native PR ordinary execution needs one stable income assessment per year."
        )
    target = candidates[0]
    if target.currency != "USD" or target.observed != date(year, 12, 31):
        raise ValueError("The full-year PR assessment is observed December31 in USD.")
    if scenario.end <= date(year, 12, 31):
        raise ValueError("PR country execution cannot omit the full-year closing assessment.")
    return target


def native_result(annual, observed):
    if observed is None:
        full = complete_annual(annual)
        case, statuses = prepare(full)
        if annual.pr_federal.gain_profile is not None:
            from wealthlab.tax.pr_execution_federal import calculate as federal
            from wealthlab.tax.pr_execution_gain_tax import assess

            return assess(full, case, statuses, federal(full), 0)
        return dict(assessment=calculate(case, recognized(case), 0), actual_us_income_tax_paid=0)
    year = annual.policy.year
    observed = closing_observation(observed, year)
    if year in observed["provisional_returns"]:
        raise ValueError("PR country settlement needs a finalized original US return.")
    position = observed["closed_returns"].get(year)
    if position is None:
        raise ValueError("PR country settlement needs a complete closed US tax year.")
    return actual(position)


def closing_observation(observations, year):
    matches = [row for row in observations if row["date"] == f"{year}-12-31"]
    if not matches:
        raise ValueError("PR country settlement needs an actual year-end observation.")
    observed, latest = matches[-1], observations[-1]
    closing = observed["closed_returns"].get(year)
    final = latest["closed_returns"].get(year)
    if (
        closing is not None
        and final is not None
        and (closing.net_paid != final.net_paid or closing.case != final.case)
    ):
        raise ValueError("Later US payment/return changes require a dated PR assessment revision.")
    return observed
