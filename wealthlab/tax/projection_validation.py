"""Reject missing tax character or annual context instead of quietly projecting untaxed cash."""

from datetime import timedelta
from decimal import Decimal

from wealthlab.tax.annual import Payments
from wealthlab.tax.projection_inputs import TaxPlan


def validate(plan: TaxPlan, scenario) -> None:
    """The typed first-year case replaces the legacy summary when tax is enabled.

    Future cases contain policy, filing and deduction assumptions; recognized
    amounts come from dated events and carries from the preceding year.
    """
    from wealthlab.tax.nj_residence_household import validate as validate_residence
    from wealthlab.tax.pr_execution_household import validate as validate_pr

    validate_residence(plan, scenario)
    validate_pr(plan, scenario)
    validate_dates(plan, scenario)
    validate_owners(plan, scenario)
    if any(scenario.ytd.model_dump().values()):
        raise ValueError(
            "With taxes enabled, enter YTD facts/payments in the first annual tax case "
            "and clear the legacy YTD summary to avoid ambiguous duplicate context."
        )
    if {rule.income_id for rule in plan.income_rules} != {item.id for item in scenario.incomes}:
        raise ValueError("Every income schedule needs one explicit federal/NJ tax-character rule.")
    for case in plan.cases:
        validate_case(case, scenario)
    for item in plan.events:
        validate_event(item)


def validate_case(case, scenario) -> None:
    """First-year base income/payments represent opening YTD; future bases are zero."""
    validate_policy(case)
    validate_filing(case, scenario)
    first = case.policy.year == scenario.start.year
    if not first and case.payments != Payments():
        raise ValueError("Future annual cases cannot contain payments already made.")
    if not first and (any(opening_amounts(case)) or case.nj_income.business.carry):
        raise ValueError(
            "Future recognized income/carries must be dated or propagated, not opening facts."
        )


def opening_amounts(case) -> list[Decimal]:
    # Nested NJ categories and owner-qualified retirement amounts also belong to
    # the opening ledger. Checking only top-level wages would miss those facts.
    models = [
        case.federal_income,
        case.nj_income,
        case.nj_income.business,
        case.nj_income.retirement,
    ]
    return [
        value
        for model in models
        for value in model.model_dump().values()
        if isinstance(value, Decimal)
    ]


def validate_event(item) -> None:
    if item.federal.short_carry or item.federal.long_carry or item.new_jersey.business.carry:
        raise ValueError("Carryforwards belong to annual opening context, not dated events.")
    if item.new_jersey.retirement.special_exclusion_eligible:
        raise ValueError("Special retirement eligibility belongs to the annual case.")


def validate_dates(plan: TaxPlan, scenario) -> None:
    years = set(range(scenario.start.year, (scenario.end - timedelta(days=1)).year + 1))
    if {case.policy.year for case in plan.cases} != years:
        raise ValueError("Provide exactly one annual tax case for every projected calendar year.")
    if any(
        not scenario.start <= event.date < scenario.end
        for event in [*plan.events, *plan.estimated_payments]
    ):
        raise ValueError("Tax events must lie inside the projection period.")


def validate_owners(plan, scenario) -> None:
    owners = dict(
        zip(
            ("wages_primary", "wages_spouse"),
            [member.id for member in scenario.members],
            strict=False,
        )
    )
    income_owners = {item.id: item.owner for item in scenario.incomes}
    for rule in plan.income_rules:
        if rule.federal.startswith("wages_") and income_owners.get(rule.income_id) != owners.get(
            rule.federal
        ):
            raise ValueError("Wage tax character must match the income owner and filing person.")


def validate_policy(case) -> None:
    case.policy.valuation()
    if case.nj_regime == "published_2025" and case.policy.year != 2025:
        raise ValueError("Choose an explicit NJ future-law assumption for years after 2025.")


def validate_filing(case, scenario) -> None:
    joint = len(scenario.members) == 2
    units = [case.filing, case.nj_filing or case.filing]
    if any((unit.status == "joint") != joint for unit in units):
        raise ValueError(
            "Household tax projections currently support one filing unit: "
            "two members must file jointly; separate returns require separate scenarios."
        )
