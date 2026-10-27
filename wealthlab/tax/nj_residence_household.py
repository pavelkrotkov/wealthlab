"""Observe one dated NJ profile inside the existing US tax and household cash ledger.

This first move profile settles positive NJ liabilities together at year end.
Unallocated prepayments across NJ-1040/NJ-1040NR cannot be netted: their separate
payment/refund identities belong to the shared jurisdiction cash-book extension.
"""

from datetime import timedelta

from wealthlab.tax import nj_residence


def observe(case, end):
    if case.nj_residence is None:
        return case
    return case.model_copy(
        update=dict(
            nj_residence=case.nj_residence.model_copy(update=dict(as_of=end - timedelta(days=1)))
        )
    )


def validate(plan, scenario):
    cases = [case for case in plan.cases if case.nj_residence is not None]
    if not cases:
        return
    validate_plan_cash(plan)
    for case in cases:
        validate_case(case, scenario)


def validate_plan_cash(plan):
    if plan.nj_wage_withholding or any(p.new_jersey for p in plan.estimated_payments):
        raise ValueError("NJ residence cash currently requires no unallocated NJ prepayments.")
    if plan.settlement_timing != "year_end":
        raise ValueError(
            "NJ residence cash requires year-end settlement until returns own payments."
        )
    validate_source_payments(plan)


def validate_case(case, scenario):
    profile = case.nj_residence
    people = dict(zip((m.id for m in scenario.members), ("primary", "spouse"), strict=False))
    if {p.id: p.role for p in profile.people} != people:
        raise ValueError("NJ residence people must match the household's stable filing roles.")
    opening = max(scenario.start, scenario.start.replace(year=case.policy.year, month=1, day=1))
    observed = observe(case, opening)
    state = nj_residence.calculate(
        observed.nj_filing or observed.filing,
        observed.nj_income,
        observed.nj_deductions,
        observed.policy.year,
        observed.nj_regime == "freeze_2025",
        profile=observed.nj_residence,
    )
    if case.payments.nj_withheld or case.payments.nj_estimates:
        raise ValueError("Opening NJ prepayments require explicit per-return allocation.")
    if state["income_tax"] < 0:
        raise ValueError("NJ residence refunds need independently allocated return payments.")


def validate_source_payments(plan):
    for event in plan.events:
        if event.withholding is not None and event.withholding.nj_withheld:
            raise ValueError("NJ residence source withholding needs per-return payment allocation.")
