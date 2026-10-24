"""Annual pro rata recovery uses the completed year's pool, not a cash-election shortcut."""

from datetime import date
from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.retirement.distribution_inputs import AccountReturn
from wealthlab.retirement.ira_household_example import synthetic


def test_jurisdiction_basis_carries_between_years():
    c = synthetic()
    owner = c.ira_plan.owners[0].model_copy(
        update=dict(federal_ira_basis=Decimal(20000), nj_ira_basis=Decimal(50000))
    )
    plan = c.ira_plan.model_copy(update=dict(owners=[owner, c.ira_plan.owners[1]]))
    rows = project(c.model_copy(update=dict(ira_plan=plan)))
    a = rows[11]["ira_annual_reconciliation"]
    b = rows[23]["ira_annual_reconciliation"]
    assert a["owners"][0]["federal_ira_basis"] == 14000
    assert a["owners"][0]["nj_ira_basis"] == 35000
    assert b["owners"][0]["federal_ira_basis"] == 10000
    assert b["owners"][0]["nj_ira_basis"] == 25000
    assert sum(r["federal_taxable"] for r in b["orders"]) == 16000
    assert sum(r["nj_taxable"] for r in b["orders"]) == 10000


def test_later_market_return_changes_annual_basis_without_creating_earlier_cash():
    c = synthetic()
    owner = c.ira_plan.owners[0].model_copy(update=dict(federal_ira_basis=Decimal(20000)))
    growth = AccountReturn(
        id="december_growth",
        provenance="assumption",
        date=date(2026, 12, 1),
        account_id="retirement",
        rate=Decimal(".5"),
    )
    plan = c.ira_plan.model_copy(
        update=dict(owners=[owner, c.ira_plan.owners[1]], returns=[growth])
    )
    rows = project(c.model_copy(update=dict(ira_plan=plan)))
    assert rows[0]["ira_withdrawal_cash"] == 20000
    assert rows[0]["account_balances"]["retirement"] == 80000
    assert rows[10]["annual_tax"]["total_liability"] == 0
    assert rows[11]["account_balances"]["retirement"] == 105000
    assert rows[11]["ira_annual_reconciliation"]["owners"][0]["federal_ira_basis"] == Decimal(
        "15555.56"
    )
