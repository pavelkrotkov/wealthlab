"""Initial search scope has ordinary liquid lots and IRA schedules with observable final exits.

Product-specific exit certificates, blended allocations and cross-border taxes
belong to subsequent integration layers; zero net product equity is not proof
that its gross positions or contingent obligations have closed.
"""

ALLOWED_PLANS = {
    "tax_plan",
    "employment_plan",
    "ira_plan",
    "medicare_plan",
    "lot_plan",
    "social_work_plan",
}


def validate(household):
    if unsupported_plans(household):
        raise ValueError(
            "This search profile supports ordinary taxable lots and IRA schedules; "
            "product/wrapper exit integration remains required."
        )
    if any(a.wrapper not in {"cash", "taxable", "traditional", "roth"} for a in household.accounts):
        raise ValueError("This search profile requires cash, taxable or ordinary IRA accounts.")


def unsupported_plans(household):
    # New product adapters must opt in with their exit semantics validated.
    return [
        key
        for key in type(household).model_fields
        if key.endswith("_plan")
        and key not in ALLOWED_PLANS
        and getattr(household, key) is not None
    ]
