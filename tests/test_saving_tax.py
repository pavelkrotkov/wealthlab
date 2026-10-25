"""Cash already owed for tax cannot be turned into an optional share investment.

The tax/cash-floor oracle is $1,200 minus $1,000 bills, $50 tax and $100 reserve:
only $50 can be invested. The wash oracle sells $120-cost shares for $100 and
buys five back, carrying exactly $100 disallowed federal loss into their basis.
"""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.saving_example import synthetic


def test_saving_reserves_actual_tax_and_a_separate_cash_floor():
    data = synthetic().model_dump(mode="json")
    data["end"] = "2026-02-01"
    data["accounts"][0]["balance"] = "1200"
    lots = data["lot_plan"]
    lots["case"]["end"] = "2026-01-31"
    lots["monthly_marks"] = lots["monthly_marks"][:1]
    lots["savings"] = lots["savings"][:1]
    lots["savings"][0]["minimum_cash"] = "100"
    data["tax_plan"]["settlement_timing"] = "monthly_accrued"
    data["tax_plan"]["cases"][0]["federal_income"]["insurance_additional_tax"] = "50"
    row = project(Scenario.model_validate(data))[0]
    assert row["saving_spent"] == 50
    assert row["closing_cash"] == 100
    assert row["tax_settlement_paid"] == 50
    assert row["tax_position"] == 0
    assert row["net_wealth"] == 150


def test_actual_saving_purchase_reuses_the_existing_wash_basis_ledger():
    data = synthetic().model_dump(mode="json")
    data["accounts"][1]["balance"] = "10000"
    case = data["lot_plan"]["case"]
    case["lots"] = [
        dict(
            id="opening",
            provenance="assumption",
            account_id="brokerage",
            security_id="stock",
            acquired="2020-01-01",
            federal_holding_start="2020-01-01",
            liquid_after="2020-01-01",
            quantity="100",
            federal_basis="12000",
            nj_basis="12000",
            economic_basis=None,
        )
    ]
    case["trades"] = [
        dict(
            id="sell",
            provenance="assumption",
            date="2026-01-31",
            action="sell",
            account_id="brokerage",
            security_id="stock",
            quantity="100",
            price="100",
            commission="0",
        )
    ]
    data["lot_plan"]["savings"] = data["lot_plan"]["savings"][:1]
    row = project(Scenario.model_validate(data))[-1]
    lot = row["lot_audit"]["lots"][0]
    assert lot["quantity"] == "5.000000"
    assert lot["federal_basis"] == "600.00"
    assert lot["nj_basis"] == "500.00"
    assert row["account_balances"]["brokerage"] == 500
    assert row["net_wealth"] == 12000
