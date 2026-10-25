"""Actual eligible transfers debit the plan once and preserve IRA chronology and taxes."""

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.workplace_rollover_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_actual_source_and_ira_assets_reconcile_without_spending_cash(rows):
    feb = rows[1]
    assert feb["account_balances"] == dict(cash=10000, work_pretax=20000, ira=90000)
    assert feb["net_wealth"] == 120000
    assert feb["ira_withdrawal_cash"] == 0
    assert feb["workplace_rollover_funded"] == 80000
    assert feb["workplace_withdrawal_gross"] == 0


def test_later_ira_draw_uses_its_own_age_rule_and_survives_next_year(rows):
    draw = rows[11]["ira_annual_reconciliation"]["orders"][0]
    assert draw["paid"] == 15000
    assert draw["additional_tax"] == 1500
    assert rows[2]["account_balances"] == dict(cash=25000, work_pretax=20000, ira=75000)
    assert rows[-1]["net_wealth"] == 118500
    assert rows[-1]["account_balances"]["ira"] == 75000
