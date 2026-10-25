"""Optional cash becomes actual shares once; commissions are an economic cost.

With flat marks, $5,000 opening cash minus $3,000 bills leaves $2,000 wealth.
Saving $500 in each of three months changes liquidity, not wealth. A $1 trade
commission reduces the acquired position and wealth by exactly $3 in total.
"""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.saving_example import synthetic


def test_saving_creates_real_lots_and_preserves_cash_and_basis():
    row = project(synthetic())[-1]
    assert row["closing_cash"] == 500
    assert row["account_balances"]["brokerage"] == 1500
    assert row["net_wealth"] == 2000
    assert sum(r["spent"] for r in row["saving_audit"]) == 1500
    assert len(row["lot_audit"]["lots"]) == 3
    assert row["lot_audit"]["lots"][0]["federal_basis"] == "500.00"


def test_commissions_reduce_invested_value_without_changing_the_cash_budget():
    data = synthetic().model_dump(mode="json")
    for saving in data["lot_plan"]["savings"]:
        saving["commission_per_trade"] = "1"
    rows = project(Scenario.model_validate(data))
    assert rows[-1]["closing_cash"] == 500
    assert rows[-1]["account_balances"]["brokerage"] == 1497
    assert rows[-1]["net_wealth"] == 1997
    assert sum(r["saving_commissions"] for r in rows) == 3


def test_optional_unfilled_saving_does_not_take_bill_cash_or_create_funding_failure():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "3000"
    for saving in data["lot_plan"]["savings"]:
        saving["minimum_cash"] = "2000"
    rows = project(Scenario.model_validate(data))
    assert sum(r["saving_spent"] for r in rows) == 0
    assert sum(r["saving_unfilled"] for r in rows) == 1500
    assert not any(r["funding_failure"] for r in rows)
    assert rows[-1]["net_wealth"] == 0
