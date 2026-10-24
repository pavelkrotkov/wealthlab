"""Independent cash conservation and annual tax timing for locked IRA schedules."""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.ira_household_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_fixed_withdrawals_conversions_and_tax_conserve_capital(rows):
    assert sum(r["ira_withdrawal_cash"] for r in rows) == 40000
    assert sum(r["ira_conversion_value"] for r in rows) == 10000
    assert rows[-1]["account_balances"] == dict(cash=39580, retirement=50000, roth=10000)
    assert rows[-1]["net_wealth"] == 200000 - 96000 - 4420
    assert not any(r["funding_failure"] for r in rows)


def test_unscheduled_ira_value_cannot_hide_spending_shortfalls():
    c = synthetic()
    accounts = [
        a.model_copy(update=dict(balance=Decimal(0))) if a.wrapper == "cash" else a
        for a in c.accounts
    ]
    result = project(c.model_copy(update=dict(accounts=accounts)))
    assert any(r["funding_failure"] for r in result)
    assert all(r["closing_cash"] >= 0 for r in result)
    assert result[-1]["account_balances"]["retirement"] == 50000
