"""Optional saving follows real product cash and preserves tax/bill liquidity.

After a $1k policy premium and $80k QOZ call, $24k remains. A $30k saving
request keeps its $1k buffer and buys only $23k of flat stock, leaving $7k
unfilled. Subsequent policy cash and annual tax still conserve the original $115k.
"""

from decimal import Decimal

from qoz_life_cases import synthetic

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_qoz_and_life_cash_precede_optional_saving_without_creating_or_losing_wealth():
    data = synthetic().model_dump(mode="json")
    linked = data["lot_plan"]
    linked["savings"] = [
        dict(
            id="after_products",
            provenance="assumption",
            date="2026-01-31",
            account_id=linked["case"]["accounts"][0]["id"],
            amount="30000",
            target_weights={linked["case"]["securities"][0]["id"]: "1"},
            commission_per_trade="0",
            minimum_cash="1000",
        )
    ]
    rows = project(Scenario.model_validate(data))
    first, final = rows[0], rows[-1]
    assert first["qoz_call_paid"] == Decimal(80000)
    assert first["life_payments_paid"] == Decimal(1000)
    assert first["saving_spent"] == Decimal(23000)
    assert first["saving_unfilled"] == Decimal(7000)
    assert first["closing_cash"] == Decimal(1000)
    assert final["account_balances"]["brokerage"] == Decimal(23000)
    assert final["net_wealth"] == Decimal(115000) - final["annual_tax"]["total_liability"]
