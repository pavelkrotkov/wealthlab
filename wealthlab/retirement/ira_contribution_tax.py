"""Check funded IRA elections against supported completed W-2 tax inputs.

The supplied MAGI forecast controls requests. A completed annual tax case must
still support the deduction actually taken and Roth deposits actually funded.
No excess-contribution correction or Social Security/passive-loss MAGI
worksheet is inferred. Without a tax case the result remains conditional.
"""

from decimal import Decimal

from wealthlab.retirement.contribution_rules import ira_limit
from wealthlab.retirement.ira_rules import deductible, phaseout, reduced

ZERO = Decimal(0)


def check(case, rows, additions, annual):
    if case.contributions is None:
        return None
    if annual is None:
        return dict(status="supplied_annual_forecasts_only")
    income = case.annual_tax_case.federal_income
    compensation = income.wages_primary + income.wages_spouse
    funded = sum((p["traditional_ira"] + p["roth_ira"] for p in additions), ZERO)
    if funded > compensation:
        raise ValueError(
            "Annual IRA funding exceeds supported W-2 compensation; "
            "other compensation needs another adapter."
        )
    magi, roth_magi = completed_magi(rows, additions, annual)
    people = {p.id: p for p in case.contributions.contributors}
    for added in additions:
        person = people[added["owner"]].model_copy(
            update=dict(traditional_ira_magi=magi, roth_ira_magi=roth_magi)
        )
        check_owner(case.contributions, person, added)
    return dict(
        status="checked_supported_annual_w2_case",
        traditional_ira_magi=magi,
        roth_ira_magi=roth_magi,
        eligible_w2_compensation=compensation,
    )


def completed_magi(rows, additions, annual):
    deduction = sum((p["federal_ira_deduction"] for p in additions), ZERO)
    magi = annual["with_distributions"]["federal"]["agi"] + deduction
    conversions = sum((r["federal_taxable"] for r in rows if r["kind"] == "conversion"), ZERO)
    roth_magi = magi - conversions
    return magi, roth_magi


def check_owner(plan, person, added):
    if deductible(plan, person, added["traditional_ira"]) != added["federal_ira_deduction"]:
        raise ValueError(
            "Completed annual IRA MAGI changes the maximum deduction; update its supplied forecast."
        )
    limit = ira_limit(person, plan)
    roth = reduced(limit, person.roth_ira_magi, phaseout(plan, person, True))
    cap = max(ZERO, min(roth, limit - added["traditional_ira"]))
    if added["roth_ira"] > cap:
        raise ValueError("Funded Roth IRA contributions exceed completed annual MAGI eligibility.")
