"""Locked tuition remains an actual bill, even while its account continues earning.

A funded household cash fallback pays the net qualified bill exactly once.
With no household cash, marked 529 wealth cannot fill the liquidity gap;
contribution basis remains intact because no distribution actually occurred.
"""

from decimal import Decimal

import pytest

from tests.wrapper_market_cases import flat, lock
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


@pytest.mark.parametrize("cash, funded", [("100000", True), ("0", False)])
def test_locked_529_uses_only_actual_household_tuition_fallback(cash, funded):
    case, market, binding = flat()
    data = case.model_dump(mode="json")
    data["accounts"][0]["balance"] = cash
    data["education_plan"]["tuition"] = [
        dict(
            id="bill",
            provenance="illustration",
            date="2026-09-01",
            source="college",
            amount="12000",
        )
    ]
    result = run(Scenario.model_validate(data), generate(lock(market)), binding)
    rows = result["details"][0]["rows"]
    assert result["outcomes"][0]["funded"] == funded
    assert rows[-1]["account_balances"]["college"] == Decimal("38047.26")
    assert sum(r["education_wrapper_paid"] for r in rows) == 0
    assert rows[8]["education_cash_fallback"] == (12000 if funded else 0)
    assert rows[-1]["education_audit"]["years"][0]["contribution_basis"]["college"] == 20000
