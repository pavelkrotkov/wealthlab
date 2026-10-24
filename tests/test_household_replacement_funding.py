"""A synthetic harvest cannot strand otherwise liquid replacement capital by accident.

Opening $101k loses $50k in the first-month price shock. Qualified replacement
purchases conserve that $51k. Spending $1,500 for 24 months uses the $1k cash,
$20k remaining original stock and $15k replacement stock, leaving $15k.
"""

from tests.market_household_cases import flat
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.policy_example import enable


def test_later_spending_can_use_the_starters_explicitly_permitted_replacement():
    case, market, binding = flat(cash_yield=0)
    data = case.model_dump(mode="json")
    data["expenses"] = [
        dict(
            id="living",
            provenance="illustration",
            start=data["start"],
            end=data["end"],
            monthly_amount="1500",
            currency="USD",
            annual_growth=0,
            category="essential",
        )
    ]
    data["lot_plan"]["funding_sources"][0]["commission"] = "0"
    case, binding = enable(Scenario.model_validate(data), binding, "Harvesting")
    paths = market.model_dump(mode="json")
    paths.update(
        mode="stress", shocks=[dict(name="early loss", month=0, mark_shocks=dict(equities=-0.5))]
    )
    result = run(case, generate(MarketCase.model_validate(paths)), binding)
    rows = result["details"][0]["rows"]
    orders = rows[-1]["lot_audit"]["funding_orders"]
    assert result["outcomes"][0]["funded"]
    assert rows[-1]["net_wealth"] == 15000
    assert sum(r["essential"] for r in rows) == 36000
    assert any(order["security_id"] == "replacement" for order in orders)
