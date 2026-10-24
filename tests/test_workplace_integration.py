"""Workplace money remains separate from IRA pro-rata pools and current-payroll owners."""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.household.records import Account
from wealthlab.retirement.ira_household_example import synthetic as ira_example
from wealthlab.retirement.workplace_example import synthetic, template
from wealthlab.retirement.workplace_inputs import WorkplacePlan


def test_workplace_balance_stays_outside_ordinary_ira_pools():
    s = ira_example()
    plan = template(s)
    plan.update(
        products=dict(employee_plan="pretax_401k"),
        complete_single_employer_elections_confirmed=True,
        gross_wages_before_deferrals_confirmed=True,
    )
    account = Account(
        id="employee_plan",
        provenance="illustration",
        owner=s.members[0].id,
        currency="USD",
        wrapper="traditional",
        balance=10000,
        monthly_fee=0,
    )
    s = s.model_copy(
        update=dict(
            accounts=[*s.accounts, account], workplace_plan=WorkplacePlan.model_validate(plan)
        )
    )
    r = project(s)[-1]
    assert r["account_balances"]["employee_plan"] == 10000
    assert r["net_wealth"] == Decimal("109580")
    assert r["ira_annual_reconciliation"]["owners"][0]["federal_ira_basis"] == 0


def test_joint_account_is_not_an_employee_plan_even_without_orders():
    s = synthetic()
    accounts = [
        a.model_copy(update=dict(owner="joint")) if a.id == "work_pretax" else a for a in s.accounts
    ]
    with pytest.raises(ValueError, match="individual household owner"):
        project(s.model_copy(update=dict(accounts=accounts)))
