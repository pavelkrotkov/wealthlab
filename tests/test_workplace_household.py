"""Gross wages reconcile to taxable income, full payroll, locked balances and cash."""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.workplace_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_funded_pretax_roth_and_unfilled_elections_share_one_limit(rows):
    last = rows[-1]
    assert last["account_balances"] == dict(
        cash=Decimal("176637"), work_pretax=Decimal("24000"), work_roth=Decimal("500")
    )
    assert sum(r["workplace_unfilled"] for r in rows) == 1500
    assert last["workplace_audit"][-1]["blocked_by_limit"] == 1500


def test_income_tax_wages_exclude_pretax_but_payroll_keeps_it(rows):
    taxes = rows[-1]["annual_tax"]
    assert (taxes["federal"]["agi"], taxes["new_jersey"]["gross_income"]) == (96000, 96000)
    # 2025 frozen joint brackets: 23850*.10 + (64500-23850)*.12.
    assert taxes["federal"]["income_tax"] == 7263
    assert taxes["federal"]["employee_payroll"] == Decimal("120000") * Decimal(".0765")


def test_employee_transfers_conserve_capital_and_do_not_become_spending(rows):
    assert rows[-1]["net_wealth"] == 100000 + 120000 - rows[-1]["annual_tax"]["total_liability"]
    assert rows[-1]["net_wealth"] == Decimal("201137")
    assert not any(r["funding_failure"] for r in rows)


def test_roth_elections_keep_wages_taxable_and_same_payroll():
    s = synthetic()
    orders = [
        o.model_copy(update=dict(kind="roth_401k", destination="work_roth"))
        for o in s.workplace_plan.orders
    ]
    s = s.model_copy(
        update=dict(workplace_plan=s.workplace_plan.model_copy(update=dict(orders=orders)))
    )
    r = project(s)[-1]
    assert r["annual_tax"]["federal"]["agi"] == 120000
    assert r["annual_tax"]["federal"]["income_tax"] == 10143
    assert (r["annual_tax"]["federal"]["employee_payroll"], r["account_balances"]["work_roth"]) == (
        9180,
        24500,
    )
