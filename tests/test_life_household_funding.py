"""Policy premiums consume actual shares through the household's existing sale solver.

A $100,000 brokerage with full cost basis and no fees funds $2,000 premiums and
$3,000 spending, offset by the $500 policy loan. Remaining shares plus net policy
value must reconcile to $107,000, with no duplicate cash deposit or policy debt.
"""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import plan
from wealthlab.products.life_household_example import synthetic


def funded_data():
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["accounts"].append(
        dict(
            id="brokerage",
            provenance="assumption",
            owner="person_a",
            wrapper="taxable",
            currency="USD",
            balance="100000",
            monthly_fee="0",
        )
    )
    data["life_plan"]["holdings"][0]["funding"] = "permitted_household_sales"
    lots = plan(Scenario.model_validate(data))
    lots["funding_sources"][0]["commission"] = "0"
    for lot in lots["case"]["lots"]:
        basis = str(Decimal(lot["quantity"]) * 100)
        lot.update(federal_basis=basis, nj_basis=basis)
    lots["case"]["closing_prices"]["stock"] = "100"
    data["lot_plan"] = lots
    return data


def test_required_premiums_sell_actual_permitted_lots_and_preserve_total_wealth():
    rows = project(Scenario.model_validate(funded_data()))
    final = rows[-1]
    assert sum(r["funding_sale_proceeds"] for r in rows) == 4500
    assert sum(r["lot_cash_swept"] for r in rows) == 4500
    assert final["account_balances"]["brokerage"] == 95500
    assert final["account_balances"]["life_policy"] == 11500
    assert final["closing_cash"] == 0
    assert final["net_wealth"] == 107000
    assert not any(r["funding_failure"] for r in rows)


def test_locked_lots_do_not_fund_the_policy_and_supplied_exit_is_received_once():
    data = funded_data()
    for lot in data["lot_plan"]["case"]["lots"]:
        lot["liquid_after"] = "2027-01-01"
    rows = project(Scenario.model_validate(data))
    assert rows[0]["life_payment_unfunded"] == 1000
    assert sum(r["funding_sale_proceeds"] for r in rows) == 0
    assert sum(r["life_cash_received"] for r in rows) == 10000
    assert rows[-1]["account_balances"]["brokerage"] == 100000
    assert rows[-1]["closing_cash"] == 7000
    assert rows[-1]["net_wealth"] == 107000
