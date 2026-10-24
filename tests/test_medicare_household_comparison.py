"""Paired fixed conversion choices retain the two-year premium consequence."""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.retirement.medicare_household_example import synthetic


def test_removing_conversion_reduces_later_irmaa_using_actual_household_return():
    case = synthetic()
    orders = [
        e.model_copy(update=dict(amount=Decimal(0))) if e.kind == "conversion" else e
        for e in case.ira_plan.orders
    ]
    changed = case.model_copy(
        update=dict(ira_plan=case.ira_plan.model_copy(update=dict(orders=orders)))
    )
    rows = project(changed)
    assert rows[24]["medicare_due"] == Decimal("885.80")
    assert sum(r["medicare_due"] for r in rows[24:]) == Decimal("10629.60")
    original = project(case)
    difference = sum(r["medicare_due"] for r in original) - sum(r["medicare_due"] for r in rows)
    assert difference == Decimal("2296.80")
