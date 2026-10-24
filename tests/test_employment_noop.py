"""A redundant 100% pay event must not create extra per-flow cent rounding."""

from datetime import date
from decimal import Decimal

from tests.test_employment_wages import gross
from wealthlab.employment.example import synthetic


def test_same_pay_change_preserves_the_baseline_cash_even_at_half_cent_boundaries():
    case = synthetic()
    salary = case.incomes[0].model_copy(update=dict(monthly_amount=Decimal(".01")))
    path = case.employment_plan.paths[0]
    same = path.changes[0].model_copy(update=dict(date=date(2026, 6, 16), multiplier=Decimal(1)))
    path = path.model_copy(update=dict(changes=[same]))
    plan = case.employment_plan.model_copy(update=dict(paths=[path]))
    changed = case.model_copy(update=dict(incomes=[salary], employment_plan=plan))
    baseline = changed.model_copy(update=dict(employment_plan=None))
    assert gross(changed) == gross(baseline) == Decimal(".12")
