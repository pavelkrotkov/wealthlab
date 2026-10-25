"""Search native accounts with executed exits and fixed conditional product assumptions.

Remaining product/wrapper adapters must establish their own closure semantics;
zero net equity does not establish the absence of gross assets or obligations.
"""

from wealthlab.optimization.contract_scope import validate as validate_option_ownership

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
    "sleeve_plan",
    "exchange_fund_plan",
    "life_plan",
    "option_plan",
    "compensation_plan",
    "advisory_fee_plan",
}


def validate(household, binding):
    if unsupported_plans(household):
        raise ValueError(
            "This search profile supports native taxable lots and retirement accounts; "
            "product/wrapper exit integration remains required."
        )
    validate_accounts(household)
    validate_product_paths(household, binding)
    validate_contract_paths(household, binding)
    validate_option_ownership(household)


def validate_accounts(household):
    if any(
        a.wrapper
        not in {
            "cash",
            "taxable",
            "traditional",
            "roth",
            "hsa",
            "education",
            "insurance",
            "employer",
        }
        for a in household.accounts
    ):
        raise ValueError(
            "This search profile requires supported cash, taxable or retirement accounts."
        )

    for wrapper, name in (
        ("hsa", "hsa_plan"),
        ("education", "education_plan"),
        ("insurance", "life_plan"),
        ("employer", "compensation_plan"),
    ):
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


def validate_product_paths(household, binding):
    sleeves = (
        {s.account_id for s in household.sleeve_plan.sleeves} if household.sleeve_plan else set()
    )
    if set(binding.sleeves) != sleeves:
        raise ValueError("Optimizer paths must bind every household sleeve.")
    if household.exchange_fund_plan and not binding.exchange_factors:
        raise ValueError("Optimizer paths require an explicit exchange-fund market binding.")


def validate_contract_paths(household, binding):
    if household.option_plan and binding.options is None:
        raise ValueError("Optimizer options require their native stock/index market binding.")
    accounts = (
        {t.account for t in household.compensation_plan.tranches}
        if household.compensation_plan
        else set()
    )
    if {item.account_id for item in binding.employers} != accounts:
        raise ValueError("Optimizer paths must bind every employer compensation account.")
