"""Conditional annual Spanish assessment; bilateral credits and household cash stay separate."""

from wealthlab.tax import spain_income, spain_scope, spain_wealth
from wealthlab.tax.spain_inputs import SpainCase


def evaluate(case: SpainCase):
    common = spain_scope.common(case)
    income_reasons = common + spain_scope.income(case)
    income = spain_income.calculate(case) if not income_reasons else None
    wealth_reasons = common + spain_scope.wealth(case)
    if income_reasons:
        wealth_reasons.append("The joint income/wealth cap requires a resolved income assessment.")
    wealth = spain_wealth.calculate(case, income) if not wealth_reasons else None
    return dict(
        person_id=case.person_id,
        liability_year=case.year,
        as_of=case.as_of.isoformat(),
        currency="EUR",
        policy=f"2025 published schedules; {case.policy}; supplied prelimited classifications",
        region=case.region,
        income=section(income_reasons, income),
        wealth=section(wealth_reasons, wealth),
        total_liability_eur=total_liability(income, wealth),
        payments=[p.model_dump(mode="json") for p in case.payments],
        recognized_payments_eur={
            kind: spain_wealth.paid(case, kind) for kind in ("irpf", "wealth", "solidarity")
        },
        full_bilateral_optimization_supported=False,
        inputs=case.model_dump(mode="json"),
    )


def section(reasons, assessment):
    return dict(
        status="blocked" if reasons else "conditional", reasons=reasons, assessment=assessment
    )


def total_liability(income, wealth):
    if income is None or wealth is None:
        return None
    return income["liability"] + wealth["wealth_liability"] + wealth["solidarity_liability"]
