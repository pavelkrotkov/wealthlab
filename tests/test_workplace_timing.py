"""Current payroll capacity cannot borrow future wages, a spouse's pay or opening assets."""

from datetime import date
from decimal import Decimal

from wealthlab.employment.example import synthetic as employment
from wealthlab.household.projection import project
from wealthlab.retirement.workplace_example import synthetic


def test_job_loss_blocks_future_elections_even_with_large_opening_cash():
    s = synthetic().model_copy(update=dict(employment_plan=employment().employment_plan))
    rows = project(s)
    assert sum(r["income"] for r in rows) == 75000
    assert sum(r["workplace_contributions"] for r in rows) == 18000
    assert rows[-1]["workplace_audit"][-1]["blocked_by_current_wages"] == 2000


def test_early_election_does_not_borrow_later_payroll_or_opening_cash():
    s = synthetic()
    first = s.workplace_plan.orders[0].model_copy(update=dict(amount=Decimal(20000)))
    s = s.model_copy(
        update=dict(workplace_plan=s.workplace_plan.model_copy(update=dict(orders=[first])))
    )
    row = project(s)[0]
    assert row["workplace_contributions"] == 10000
    assert row["closing_cash"] < 100000  # Payroll taxes still must be funded.
    assert row["account_balances"]["work_pretax"] == 10000


def test_two_destinations_cannot_spend_the_same_months_wages_twice():
    s = synthetic()
    first = s.workplace_plan.orders[0].model_copy(update=dict(amount=Decimal(8000)))
    second = s.workplace_plan.orders[-1].model_copy(
        update=dict(date=date(2026, 1, 15), amount=Decimal(8000))
    )
    s = s.model_copy(
        update=dict(workplace_plan=s.workplace_plan.model_copy(update=dict(orders=[first, second])))
    )
    row = project(s)[0]
    assert row["workplace_contributions"] == 10000
    assert (row["account_balances"]["work_pretax"], row["account_balances"]["work_roth"]) == (
        8000,
        2000,
    )


def test_spouses_gross_pay_cannot_replace_the_owners_missing_payroll():
    s = synthetic()
    own = s.incomes[0].model_copy(update=dict(monthly_amount=Decimal(0)))
    spouse = own.model_copy(
        update=dict(id="spouse_salary", owner="person_b", monthly_amount=Decimal(50000))
    )
    from wealthlab.tax.projection_inputs import IncomeRule

    taxes = s.tax_plan.model_copy(
        update=dict(
            income_rules=[
                *s.tax_plan.income_rules,
                IncomeRule(income_id="spouse_salary", federal="wages_spouse", new_jersey="wages"),
            ]
        )
    )
    rows = project(s.model_copy(update=dict(incomes=[own, spouse], tax_plan=taxes)))
    assert sum(r["workplace_contributions"] for r in rows) == 0
    assert rows[-1]["workplace_audit"][-1]["blocked_by_current_wages"] == 2000
