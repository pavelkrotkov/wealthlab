"""Rehiring, independent bonuses and unchanged annual growth are concrete policy choices."""

from datetime import date
from decimal import Decimal

from tests.test_employment_wages import gross
from wealthlab.employment.example import synthetic
from wealthlab.employment.inputs import WageChange
from wealthlab.employment.wages import prepare
from wealthlab.household.flows import earnings
from wealthlab.tax.projection_inputs import IncomeRule


def test_return_to_work_sets_a_new_baseline_multiplier_after_job_loss():
    case = synthetic()
    path = case.employment_plan.paths[0]
    returning = WageChange(
        id="rehire",
        provenance="illustration",
        date=date(2026, 12, 1),
        kind="return_to_work",
        multiplier=1,
    )
    path = path.model_copy(update=dict(changes=[*path.changes, returning]))
    plan = case.employment_plan.model_copy(update=dict(paths=[path]))
    assert gross(case.model_copy(update=dict(employment_plan=plan))) == 85000


def test_only_selected_bonus_streams_follow_the_job_policy():
    case = synthetic()
    bonus = case.incomes[0].model_copy(
        update=dict(
            id="bonus", start=date(2026, 9, 1), end=date(2026, 10, 1), monthly_amount=Decimal(1000)
        )
    )
    rule = IncomeRule(income_id="bonus", federal="wages_primary", new_jersey="wages")
    tax = case.tax_plan.model_copy(update=dict(income_rules=[*case.tax_plan.income_rules, rule]))
    case = case.model_copy(update=dict(incomes=[*case.incomes, bonus], tax_plan=tax))
    assert gross(case) == 76000
    path = case.employment_plan.paths[0].model_copy(update=dict(income_ids=["salary", "bonus"]))
    plan = case.employment_plan.model_copy(update=dict(paths=[path]))
    assert gross(case.model_copy(update=dict(employment_plan=plan))) == 75500


def test_pay_change_does_not_restart_the_scenario_growth_clock():
    case = synthetic()
    salary = case.incomes[0].model_copy(update=dict(annual_growth=0.10))
    changed = prepare(case.model_copy(update=dict(incomes=[salary])))
    # Compare against the same baseline amount/date/growth, with half salary;
    # the July event must not reset elapsed growth to zero.
    baseline = case.model_copy(update=dict(employment_plan=None, incomes=[salary]))
    full = earnings(baseline, date(2026, 8, 1), date(2026, 9, 1))
    assert earnings(changed, date(2026, 8, 1), date(2026, 9, 1)) == (full / 2).quantize(
        Decimal(".01")
    )
