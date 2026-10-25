"""Actual QOZ and policy cash share one wallet and annual return.

The $115k original combined capital ends at $115k less actual tax: premiums
move cash into the policy, its $500 loan reduces surrender equity once, and
the separate $80k QOZ subscription/sale cannot duplicate assets or recognition.
"""

from calendar import monthrange
from datetime import date
from decimal import Decimal

import pytest
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_household_calendar import reserve_end
from wealthlab.products.life_household_example import synthetic as life_example


@pytest.fixture(scope="module")
def mixed_rows():
    case = flat(2026)
    data, other = case.model_dump(mode="json"), life_example().model_dump(mode="json")
    data["accounts"].append(other["accounts"][-1])
    data["life_plan"] = other["life_plan"]
    holding = data["life_plan"]["holdings"][0]
    values = holding["contract"]["values"]
    last = dict(values[-1])
    values.extend(
        dict(last, date=date(2026, month, monthrange(2026, month)[1]).isoformat())
        for month in range(4, 13)
    )
    holding["payments_complete_through"] = reserve_end(case.end, case.reserve_years).isoformat()
    return project(Scenario.model_validate(data))


def test_qoz_and_life_share_actual_cash(mixed_rows):
    rows = mixed_rows
    assert [r["closing_cash"] for r in rows[:3]] == list(map(Decimal, (24000, 23000, 23500)))
    assert rows[0]["qoz_call_paid"] == Decimal(80000)
    assert rows[0]["life_payments_paid"] == rows[1]["life_payments_paid"] == Decimal(1000)
    assert rows[2]["life_cash_received"] == Decimal(500)


def test_one_annual_return_and_policy_debt_preserve_combined_wealth(mixed_rows):
    rows = mixed_rows
    final = rows[-1]
    assert final["account_balances"]["life_policy"] == Decimal(11500)
    assert final["annual_tax"]["federal"]["agi"] == Decimal(80000)
    assert final["annual_tax"]["new_jersey"]["total_income"] == Decimal(70000)
    assert final["net_wealth"] == Decimal(115000) - final["annual_tax"]["total_liability"]
    assert {"qoz_audit", "life_policy_audit"} <= final.keys()
    assert not any(r["funding_failure"] for r in rows)
