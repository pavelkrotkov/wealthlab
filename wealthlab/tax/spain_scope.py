"""Unsupported residence and product classifications block affected results, never imply zero."""

from wealthlab.tax.spain_regional_policy import REGIONS, relief_reasons


def common(case):
    tests = (
        (
            case.residence == "full_year_resident",
            "A confirmed full-year ordinary resident is required.",
        ),
        (case.filing == "individual", "Joint/family aggregation requires another adapter."),
        (
            case.region in REGIONS,
            "Select a supported common-regime region; foral/city profiles need another adapter.",
        ),
        (
            case.worldwide_inputs_complete_confirmed,
            "Confirm complete worldwide income and fiscal assets.",
        ),
    )
    return [reason for valid, reason in tests if not valid]


def income(case):
    reasons = (
        [] if case.recognition_prelimited_confirmed else ["Confirm prelimited recognized bases."]
    )
    for item in case.incomes:
        if case.citizenship == "unknown" and item.treaty_treatment != "none":
            reasons.append(f"Income {item.id}: treaty citizenship profile is unresolved.")
        if "unknown" in (item.spanish_base, item.treatment, item.treaty_treatment):
            reasons.append(f"Income {item.id}: unresolved Spanish or treaty classification.")
        if item.spanish_base == "exempt_with_progression":
            reasons.append(f"Income {item.id}: exemption with progression needs another adapter.")
    return reasons


def wealth(case):
    return relief_reasons(case) + [
        f"Asset {asset.id}: resolve independent Spanish exemption and productivity classification."
        for asset in case.assets
        if asset.treatment == "unknown" or asset.nonproductive is None
    ]
