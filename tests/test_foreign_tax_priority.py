"""Required foreign tax precedes optional saving and reuses actual sale/basis machinery.

Paying $11,000 tax leaves $39,000 of the same $50,000 starting capital to buy
shares. The unfilled saving request creates neither capital nor unpaid tax.
A separate case funds the payment from real US lots; missing foreign basis
and source classifications remain unsupported despite successful cash payment.
"""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import plan
from wealthlab.tax.foreign_tax_example import synthetic


def broker_case(balance):
    data = synthetic().model_dump(mode="json")
    data["end"] = "2025-11-01"
    data["accounts"].append(
        dict(
            id="brokerage",
            owner="person_a",
            wrapper="taxable",
            currency="USD",
            monthly_fee="0",
            balance=str(balance),
            provenance="assumption",
        )
    )
    data["lot_plan"] = plan(Scenario.model_validate(data))
    data["lot_plan"]["case"]["closing_prices"]["stock"] = "100"
    data["lot_plan"]["monthly_marks"][0]["prices"]["stock"] = "100"
    return data


def test_foreign_tax_gets_cash_before_an_optional_saving_request():
    data = broker_case(0)
    lots = data["lot_plan"]
    lots["case"]["lots"], lots["funding_sources"] = [], []
    lots["savings"] = [
        dict(
            id="optional_buy",
            provenance="assumption",
            date="2025-10-31",
            account_id="brokerage",
            amount="50000",
            target_weights={"stock": "1"},
            commission_per_trade="0",
            minimum_cash="0",
        )
    ]
    row = project(Scenario.model_validate(data))[0]
    assert row["foreign_tax_paid"] == Decimal(11000)
    assert row["saving_spent"] == Decimal(39000)
    assert row["saving_unfilled"] == Decimal(11000)
    assert row["account_balances"]["brokerage"] == Decimal(39000)
    assert row["net_wealth"] == Decimal(39000) - row["tax_position"]


def test_existing_us_lot_funding_does_not_invent_foreign_gain_or_basis():
    data = broker_case(100000)
    data["accounts"][0]["balance"] = "0"
    data["foreign_tax_plan"]["allow_household_sales"] = True
    row = project(Scenario.model_validate(data))[0]
    assert row["foreign_tax_paid"] == Decimal(11000)
    assert row["funding_sale_proceeds"] == Decimal(11000)
    assert row["foreign_tax_position"] == 0
    assert row["annual_tax"]["federal"]["foreign_tax_credit"] == 0
    assert any("independent foreign" in r for r in row["foreign_tax_unresolved"])
    assert row["funding_failure"]


def test_new_actual_funding_gain_cannot_leave_the_known_us_bill_underfunded_by_a_stale_credit():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "7000"
    data["accounts"].append(
        dict(
            id="brokerage",
            owner="person_a",
            wrapper="taxable",
            currency="USD",
            monthly_fee="0",
            balance="100000",
            provenance="assumption",
        )
    )
    data["lot_plan"] = plan(Scenario.model_validate(data))
    lots = data["lot_plan"]
    for lot in lots["case"]["lots"]:
        lot["liquid_after"] = "2025-12-01"
    for mark in lots["monthly_marks"]:
        mark["prices"]["stock"] = "100"
    lots["case"]["closing_prices"]["stock"] = "100"
    data["foreign_tax_plan"]["allow_household_sales"] = True
    row = project(Scenario.model_validate(data))[-1]
    assert row["foreign_tax_position"] == 0
    assert row["tax_unfunded"] == 0
    assert row["tax_settlement_payment_gap"] == 0
    assert row["annual_tax"]["federal"]["foreign_tax_credit"] == 0
    assert row["foreign_tax_unresolved"]
