"""Funded payroll deposits compound inside the plan without altering wages or cash taxes."""

from decimal import Decimal

import pytest

from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.workplace_example import synthetic


@pytest.fixture(scope="module")
def result():
    household, market, binding = synthetic()
    data = market.model_dump(mode="json")
    data["assets"][0].update(expected_annual_mark_return=1.02**12 - 1, annual_cash_yield=0)
    data["expected_annual_inflation"] = 0
    return run(household, generate(MarketCase.model_validate(data)), binding)


def test_month_end_returns_follow_only_actual_funded_deposits(result):
    rows = result["details"][0]["rows"]
    pretax = Decimal(0)
    for _ in range(12):
        pretax += 2000
        pretax += (pretax * Decimal(".02")).quantize(Decimal(".01"))
    last = rows[-1]
    assert rows[0]["account_balances"]["work_pretax"] == 2040
    assert last["account_balances"]["work_pretax"] == pretax
    assert last["account_balances"]["work_roth"] == 510
    assert sum(r["workplace_contributions"] for r in rows) == 24500
    assert sum(r["workplace_unfilled"] for r in rows) == 1500
