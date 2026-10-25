"""Search scope includes native liquid lots, IRA/workplace plans, HSA and 529 books.

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
    "workplace_plan",
    "hsa_plan",
    "education_plan",
}


def validate(household):
    if unsupported_plans(household):
        raise ValueError(
            "This search profile supports native taxable lots and retirement accounts; "
            "product/wrapper exit integration remains required."
        )
    validate_accounts(household)


def validate_accounts(household):
    if any(
        a.wrapper not in {"cash", "taxable", "traditional", "roth", "hsa", "education"}
        for a in household.accounts
    ):
        raise ValueError(
            "This search profile requires supported cash, taxable or retirement accounts."
        )

    for wrapper, name in (("hsa", "hsa_plan"), ("education", "education_plan")):
        if (
            any(a.wrapper == wrapper for a in household.accounts)
            and getattr(household, name) is None
        ):
            raise ValueError(f"Optimizer {wrapper} accounts require a configured {name}.")


def unsupported_plans(household):
    # New product adapters must opt in with their exit semantics validated.
    return [
        key
        for key in type(household).model_fields
        if key.endswith("_plan")
        and key not in ALLOWED_PLANS
        and getattr(household, key) is not None
    ]
