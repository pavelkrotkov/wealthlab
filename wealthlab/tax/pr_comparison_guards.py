"""Keep unsupported incentive credit/deduction paths explicit instead of inventing treatment."""

from wealthlab.tax.pr_decree import qualification


def profile(comparison):
    reasons = []
    annual = comparison.annual
    if annual.pr_allowed_deductions or annual.pr_abt_allowed_deductions:
        reasons.append("Preferential comparison currently requires zero additional PR deductions.")
    if comparison.prior_abt_credit:
        reasons.append("Prior ABT credit consumption requires its separately reconciled history.")
    for asset in comparison.gains:
        if asset.pr_resident_since != annual.primary.local_start:
            reasons.append("Asset local residence date must reconcile to its owner's local start.")
    return reasons


def incentive(comparison):
    result = qualification(comparison.decree, comparison.annual)
    decree = comparison.decree
    if decree.residence_since != comparison.annual.primary.local_start:
        result["reasons"].append(
            "Decree residence must reconcile to the supplied local start date."
        )
    if (
        decree.application_date
        and decree.application_date.year >= 2027
        and comparison.other_preferential_entitlement != "fails"
    ):
        result["reasons"].append(
            "New 4% profile requires an explicit no-other-favorable-treatment claim."
        )
    result["eligible"] = not result["reasons"]
    return result
