"""Pure annual assessment/obligation bridge; the external foreign-tax book owns cash.

Assessment identity survives a rerun with newly observed payments or refunds.
The schedule never enters those observations or creates an actual-paid credit.
"""

from decimal import Decimal

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_assessment_inputs import SpainAssessmentPlan

TAXES = ("irpf", "wealth", "solidarity")
ZERO = Decimal(0)


def evaluate_plan(plan: SpainAssessmentPlan):
    annuals = {a.id: assessment(a) for a in plan.annuals}
    scheduled = [obligation(plan, item, annuals[item.assessment_id]) for item in plan.obligations]
    totals = [a["result"]["total_liability_eur"] for a in annuals.values()]
    complete = all(value is not None for value in totals)
    return dict(
        as_of=plan.as_of.isoformat(),
        currency="EUR",
        assessments=annuals,
        obligations=scheduled,
        total_liability_eur=sum(totals, ZERO) if complete else None,
        all_assessments_resolved=complete,
        all_obligations_resolved=all(item["status"] == "conditional" for item in scheduled),
        cash_execution_supported=False,
        full_bilateral_optimization_supported=False,
        inputs=plan.model_dump(mode="json"),
    )


def assessment(annual):
    """Reconcile annual liability against recognized tax, preserving the separate cash records."""
    result = evaluate(annual.case)
    liabilities = dict.fromkeys(TAXES)
    if result["income"]["assessment"] is not None:
        liabilities["irpf"] = result["income"]["assessment"]["liability"]
    if result["wealth"]["assessment"] is not None:
        wealth = result["wealth"]["assessment"]
        liabilities.update(
            wealth=wealth["wealth_liability"], solidarity=wealth["solidarity_liability"]
        )
    paid = result["recognized_payments_eur"]
    return dict(
        id=annual.id,
        person_id=annual.case.person_id,
        liability_year=annual.case.year,
        assessment_as_of=annual.case.as_of.isoformat(),
        liabilities_eur=liabilities,
        outstanding_eur={
            k: None if v is None else max(ZERO, v - paid[k]) for k, v in liabilities.items()
        },
        overpayment_eur={
            k: None if v is None else max(ZERO, paid[k] - v) for k, v in liabilities.items()
        },
        refund_entitlement_inferred=False,
        source_income_ids=[i.id for i in annual.case.incomes],
        result=result,
    )


def obligation(plan, item, annual):
    outstanding = annual["outstanding_eur"][item.tax_type]
    total_scheduled = sum(
        (
            i.amount_eur
            for i in plan.obligations
            if (i.assessment_id, i.tax_type) == (item.assessment_id, item.tax_type)
        ),
        ZERO,
    )
    reasons = []
    if outstanding is None:
        reasons.append("The relevant annual assessment is blocked.")
    elif total_scheduled > outstanding:
        reasons.append("Remaining schedules exceed outstanding tax; update allocations.")
    return dict(
        **item.model_dump(mode="json"),
        owner_id=annual["person_id"],
        liability_year=annual["liability_year"],
        status="blocked" if reasons else "conditional",
        reasons=reasons,
        assessment_outstanding_eur=outstanding,
        fundable_eur=None if reasons else item.amount_eur,
        overdue=item.due_date < plan.as_of,
        execution="unexecuted; the foreign-tax book owns actual payment/refund allocations",
    )
