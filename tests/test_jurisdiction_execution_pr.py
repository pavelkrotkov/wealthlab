"""Actual country liabilities replace guessed bills without another wallet or credit."""

from datetime import date
from decimal import Decimal

import pytest
from pr_execution_helpers import household

from wealthlab.tax.jurisdiction_execution import evaluate


def scenario(government=False):
    base = household(government, credit_eligibility="allowed" if government else "denied")
    plan = base.foreign_tax_plan
    assessment = plan.assessments[0].model_copy(update=dict(observed=date(2025, 12, 31)))
    schedule = plan.schedules[0].model_copy(
        update=dict(due_date=date(2025, 12, 31), requested_native=Decimal(50000))
    )
    from wealthlab.tax.foreign_tax_inputs import ForeignTaxPlan

    plan = ForeignTaxPlan.model_validate(
        plan.model_copy(update=dict(assessments=[assessment], schedules=[schedule])).model_dump()
    )
    return base.model_copy(update=dict(foreign_tax_plan=plan))


def test_native_pr_bill_and_actual_us_paid_credit_reconcile_real_cash_once():
    result = evaluate(scenario(government=True))
    final = result["rows"][-1]
    audit = result["country_assessments"]["es_income_2025"]
    assert audit["creditable_us_tax_after_federal_credit"] == Decimal("6724.50")
    assert final["foreign_tax_paid"] == audit["assessment"]["income_tax"]
    assert final["foreign_tax_paid"] != 10000
    total = sum(
        r["foreign_tax_paid"]
        + r["tax_settlement_paid"]
        + r["tax_withheld"]
        + r["tax_estimates_paid"]
        + r["prior_tax_paid"]
        for r in result["rows"]
    )
    assert final["closing_cash"] == 50000 - total
    assert not final["funding_failure"]
    assert (
        result["reconciliation"][-1]["assessments"]
        == result["reconciliation"][-1]["revised_assessments"]
    )


def test_nonconvergence_cannot_return_a_favorable_candidate():
    with pytest.raises(ValueError, match="did not converge"):
        evaluate(scenario(government=True), max_passes=1)
