"""Live annual policy/people own US credits and derive future carry vintages once.

Source roles follow the household's actual member order; a filing unit cannot
swap people merely because aggregate income reconciles. Future paid cash and
opening carries cannot be supplied again after the book derives actual history.
State deductions changed after the credit calculation need their own allocation
profile instead of retaining an earlier standard-deduction source limit.
"""


def validate_profiles(plan, scenario):
    from wealthlab.tax.foreign_tax_validation import unique

    years = [p.annual.policy.year for p in plan.credit_profiles]
    unique(years, "annual credit profile")
    required = {c.policy.year for c in scenario.tax_plan.cases}
    if set(years) != required:
        raise ValueError("Provide one foreign source/credit profile per household tax year.")
    owners = dict(zip((m.id for m in scenario.members), ("primary", "spouse"), strict=False))
    if any(p.people != owners for p in plan.credit_profiles):
        raise ValueError("Foreign credit profiles must retain the household's stable people.")
    validate_payment_ownership(plan)
    validate_deduction_timing(plan, scenario)


def validate_payment_ownership(plan):
    if any(p.tax_cash for p in plan.credit_profiles):
        raise ValueError("Actual foreign payment history belongs once in the shared cash plan.")


def validate_credit_ownership(plan, scenario):
    cases = {c.policy.year: c for c in scenario.tax_plan.cases}
    for profile in plan.credit_profiles:
        case = cases[profile.annual.policy.year]
        validate_owner(profile, case, min(cases))


def validate_owner(profile, case, first_year):
    if case.filing != profile.annual.filing or case.policy != profile.annual.policy:
        raise ValueError("Source credit profiles must match the actual filing/policy year.")
    if case.foreign_credits.regular or case.foreign_credits.alternative_minimum:
        raise ValueError("The shared foreign book must own its credit without another input claim.")
    if profile.annual.policy.year != first_year and profile.opening_carries:
        raise ValueError("Future opening foreign carries derive once from actual prior-year use.")


def validate_deduction_timing(plan, scenario):
    if scenario.tax_plan.state_deduction_mode == "actual_payments" and any(
        p.eligibility == "allowed" for p in plan.credit_profiles
    ):
        raise ValueError(
            "This derived ordinary FTC profile requires entered state deductions; "
            "post-credit settlement deductions need a separate allocation/reconciliation profile."
        )
