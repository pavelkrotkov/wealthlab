"""Dated work policies preserve actual household cash/tax accounting and retirement cutoffs."""

from datetime import date
from decimal import Decimal

from wealthlab.employment.example import synthetic
from wealthlab.employment.wages import prepare
from wealthlab.household.calendar import months
from wealthlab.household.flows import earnings
from wealthlab.household.projection import project
from wealthlab.household.storage import loads


def gross(case):
    prepared = prepare(case)
    return sum(earnings(prepared, start, end) for start, end in months(case.start, case.end))


def test_reduced_work_and_job_loss_reconcile_cash_and_annual_taxes():
    # Independent frozen-2025 check: $75k wages, $5,737.50 employee payroll,
    # $4,743 federal income tax and $1,401 NJ tax. The NJ $73,000-$73,050
    # taxable-income band uses the published whole-dollar table, not a
    # continuous marginal-bracket calculation that would differ by $1.
    rows = project(synthetic())
    assert sum(r["income"] for r in rows) == 75000
    assert rows[11]["annual_tax"]["federal"]["agi"] == 75000
    assert rows[11]["annual_tax"]["federal"]["employee_payroll"] == Decimal("5737.50")
    assert rows[11]["annual_tax"]["total_liability"] == Decimal("11881.50")
    assert rows[-1]["closing_cash"] == Decimal("67118.50")
    assert rows[-1]["net_wealth"] == Decimal("167118.50")


def test_partial_month_uses_existing_daily_accrual_and_changes_are_baseline_multiples():
    case = synthetic()
    path = case.employment_plan.paths[0]
    first = path.changes[0].model_copy(update=dict(date=date(2026, 1, 16)))
    path = path.model_copy(update=dict(changes=[first]))
    plan = case.employment_plan.model_copy(update=dict(paths=[path]))
    prepared = prepare(case.model_copy(update=dict(employment_plan=plan)))
    assert earnings(prepared, date(2026, 1, 1), date(2026, 2, 1)) == Decimal("7419.36")
    assert earnings(prepared, date(2026, 2, 1), date(2026, 3, 1)) == 5000
    assert earnings(prepared, date(2027, 1, 1), date(2027, 2, 1)) == 0


def test_round_trip_and_repeated_materialization_do_not_duplicate_wages():
    case = synthetic()
    assert loads(case.model_dump_json()) == case
    prepared = prepare(case)
    assert prepare(prepared) == prepared
    assert prepared.employment_plan is None
    assert case.employment_plan is not None
    assert case.incomes[0].monthly_amount == 10000
    assert gross(case) == 75000
