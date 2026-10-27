"""Ordinary/denied-decree alternative remains independent of conditional Act60 qualification."""

from wealthlab.tax.annual import evaluate as mainland
from wealthlab.tax.pr_annual import LIMITATION
from wealthlab.tax.pr_comparison_guards import incentive, profile
from wealthlab.tax.pr_guards import guards
from wealthlab.tax.pr_incentive_candidate import calculate
from wealthlab.tax.pr_inputs import validate
from wealthlab.tax.pr_residence import federal_status


def evaluate(comparison):
    annual = comparison.annual
    validate(annual)
    baseline = mainland(annual.baseline)
    statuses = {
        owner: federal_status(getattr(annual, owner), annual.baseline.policy.year)
        for owner in {row.owner for row in annual.income}
    }
    reasons = guards(annual, allow_gains=True) + profile(comparison)
    reasons += [reason for status in statuses.values() for reason in status["reasons"]]
    qualification = incentive(comparison)
    result = dict(
        baseline=baseline,
        configuration=comparison.model_dump(mode="json"),
        residence=statuses,
        reasons=reasons,
        qualification=qualification,
        limitation=LIMITATION,
        ordinary=None,
        incentive=None,
    )
    if reasons:
        return result
    # Denial or missing decree facts must not suppress the independent ordinary
    # alternative. Both alternatives use the same receipts and source history.
    try:
        result["ordinary"] = calculate(comparison, baseline, statuses)
    except ValueError as error:
        reasons.append(str(error))
    if qualification["eligible"]:
        calculate_incentive(comparison, baseline, statuses, result)
    return result


def calculate_incentive(comparison, baseline, statuses, result):
    try:
        candidate: dict = calculate(comparison, baseline, statuses, incentivized=True)
        ordinary = result["ordinary"]
        if (
            ordinary
            and ordinary["puerto_rico"]["income_tax"] < candidate["puerto_rico"]["income_tax"]
        ):
            candidate = dict(
                ordinary, tax_treatment_selected="More favorable supported ordinary law"
            )
        candidate["conditional"] |= result["qualification"]["conditional"]
        cost = comparison.decree.annual_compliance_cost
        candidate["annual_compliance_cost"] = cost
        candidate["tax_plus_supplied_compliance_cost"] = (
            candidate["federal_pr_payroll_total"] + cost if cost is not None else None
        )
        result["incentive"] = candidate
    except ValueError as error:
        result["qualification"]["reasons"].append(str(error))
