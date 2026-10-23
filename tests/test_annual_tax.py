"""Annual payment reconciliation conserves liability across jurisdiction/payroll buckets."""

from decimal import Decimal

from wealthlab.tax.annual import Payments, evaluate, synthetic
from wealthlab.tax.policy import TaxPolicy


def test_payments_change_balance_not_liability():
    case = synthetic()
    before = evaluate(case)
    updated = case.model_copy(
        update={
            "payments": Payments(
                federal_income_withheld=Decimal(30000),
                federal_estimates=Decimal(1000),
                employee_payroll_withheld=Decimal("13818.20"),
                nj_withheld=Decimal(9000),
            )
        }
    )
    after = evaluate(updated)
    assert before["total_liability"] == Decimal("49286.30")
    assert after["total_liability"] == before["total_liability"]
    assert after["payroll_balance"] == 0
    assert after["total_balance"] == Decimal("-4531.90")


def test_explicit_future_freeze_preserves_nominal_tax():
    case = synthetic()
    expected = evaluate(case)
    future = case.model_copy(
        update={
            "policy": TaxPolicy(year=2050, mode="freeze_2025", annual_index=0),
            "nj_regime": "freeze_2025",
        }
    )
    result = evaluate(future)
    assert result["total_liability"] == expected["total_liability"]
    assert "Hypothetical" in result["federal"]["policy"]
    assert "2050" in result["new_jersey"]["policy"]
