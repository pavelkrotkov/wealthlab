"""Actual shares, cash tax and commissions reconcile independently of basis gains.

The household opens with $101k, receives $60k wages, spends $120k and pays
$8,872 tax plus 22 sale commissions. Only the unsold shares receive the second
year's 30% mark increase. Changing tax basis never creates new asset value.
"""

from decimal import Decimal

import pytest

from wealthlab.household.calendar import money
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_wealth_conserves_real_cash_and_unsold_mark_growth(rows):
    taxes = rows[11]["annual_tax"]["total_liability"] + rows[-1]["annual_tax"]["total_liability"]
    growth = money(rows[11]["account_balances"]["brokerage"] * Decimal(".30"))
    assert taxes == 8872
    assert rows[-1]["net_wealth"] == 101000 + 60000 + growth - 120000 - taxes - 22
    assert rows[-1]["net_wealth"] == Decimal("59831.70")
    assert not any(r["funding_failure"] for r in rows)


def test_hifo_uses_actual_high_basis_shares_and_preserves_the_other_lot(rows):
    audit = rows[-1]["lot_audit"]
    assert {r["lot_id"] for r in audit["disposals"]} == {"high_basis"}
    low, high = audit["lots"]
    assert (low["quantity"], low["federal_basis"], low["nj_basis"]) == ("400", "4000", "6000")
    assert high["quantity"] == "60.243843"
    assert high["federal_basis"] == "5421.95"
    assert high["nj_basis"] == "4819.50"


def test_separate_jurisdiction_basis_feeds_the_actual_annual_returns(rows):
    audit = rows[-1]["lot_audit"]["recognized_by_year"]
    assert audit[2026][0]["long_term"] == Decimal("748.10")
    assert audit[2026][1] == Decimal("1506.20")
    assert audit[2027][0]["long_term"] == Decimal("18545.85")
    assert audit[2027][1] == Decimal("23185.30")


def test_sale_proceeds_and_taxes_are_not_deposited_twice(rows):
    assert sum(r["funding_sale_proceeds"] for r in rows) == 67872
    assert sum(r["lot_funding_proceeds"] for r in rows) == 67872
    assert sum(r["lot_cash_swept"] for r in rows) == 67872
    assert sum(r["tax_event_cash"] for r in rows) == 0
    assert sum(r["essential"] for r in rows) == 120000


def test_initial_brokerage_cash_sweeps_without_duplicating_opening_capital(rows):
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["accounts"][1]["balance"] = "101000"
    data["lot_plan"]["case"]["accounts"][0]["cash"] = "1000"
    swept = project(Scenario.model_validate(data))
    assert swept[0]["lot_cash_swept"] == 1000
    assert swept[-1]["net_wealth"] == rows[-1]["net_wealth"]
    assert sum(r["lot_cash_swept"] for r in swept) == 68872
